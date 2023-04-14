from time import sleep

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from test_utils.auth import client_auth
from users.models import AuthCode, ConfirmCode
from users.services import generate_confirm_code

User = get_user_model()


class TestAuth(APITestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.confirmed_test_user = User(
            username='test1',
            email='test1@mail.ru',
            is_active=1,
            is_confirm=1
        )
        cls.confirmed_test_user_password = '12345'
        cls.confirmed_test_user.set_password(cls.confirmed_test_user_password)
        cls.confirmed_test_user.save()

        cls.unconfirmed_test_user = User(
            username='test2',
            email='test2@mail.ru',
            is_active=1,
            is_confirm=0
        )
        cls.unconfirmed_test_user_password = '12345678'
        cls.unconfirmed_test_user.set_password(
            cls.unconfirmed_test_user_password
        )
        cls.unconfirmed_test_user.save()

        cls.guest_client = cls.client_class()
        cls.confirmed_auth_user_client = cls.client_class()
        client_auth(
            client=cls.confirmed_auth_user_client,
            username=cls.confirmed_test_user.username,
            email=cls.confirmed_test_user.email,
        )
        cls.unconfirmed_auth_user_client = cls.client_class()
        client_auth(
            client=cls.unconfirmed_auth_user_client,
            username=cls.unconfirmed_test_user.username,
            email=cls.unconfirmed_test_user.email,
        )
        super().setUpTestData()

    def test_01_guest_login_with_email(self):
        response = self.guest_client.post(
            reverse('login'),
            data={'email': self.confirmed_test_user.email}
        )
        self.assertEqual(response.status_code, 200)

    def test_02_guest_login_without_email(self):
        response = self.guest_client.post(reverse('login'))
        self.assertEqual(response.status_code, 400)

    def test_03_guest_get_token(self):
        self.guest_client.post(
            reverse('login'),
            data={'email': self.confirmed_test_user.email}
        )
        auth_code = AuthCode.objects.get(
            user__email=self.confirmed_test_user.email
        ).code
        response = self.guest_client.post(
            reverse('token'),
            data={
                'auth_code': auth_code, 'email': self.confirmed_test_user.email
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json()['access_token']), str)
        self.assertEqual(type(response.json()['refresh_token']), str)

    def test_04_guest_get_token_with_incorrect_auth_token(self):
        self.guest_client.post(
            reverse('login'),
            data={'email': self.confirmed_test_user.email}
        )
        auth_code = AuthCode.objects.get(
            user__email=self.confirmed_test_user.email
        ).code
        response = self.guest_client.post(
            reverse('token'),
            data={
                'auth_code': auth_code - 1,
                'email': self.confirmed_test_user.email
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_05_guest_get_token_with_incorrect_email(self):
        self.guest_client.post(
            reverse('login'),
            data={'email': self.confirmed_test_user.email}
        )
        auth_code = AuthCode.objects.get(
            user__email=self.confirmed_test_user.email
        ).code
        response = self.guest_client.post(
            reverse('token'),
            data={'auth_code': auth_code, 'email': 'test'}
        )
        self.assertEqual(response.status_code, 400)

    def test_06_guest_get_refresh_token(self):
        self.guest_client.post(
            reverse('login'),
            data={'email': self.confirmed_test_user.email}
        )
        auth_code = AuthCode.objects.get(
            user__email=self.confirmed_test_user.email
        ).code
        response = self.guest_client.post(
            reverse('token'),
            data={
                'auth_code': auth_code,
                'email': self.confirmed_test_user.email
            }
        ).json()
        old_access_token = response['access_token']
        old_refresh_token = response['refresh_token']
        sleep(1)
        response = self.guest_client.post(
            reverse('refresh'),
            data={'refresh_token': old_refresh_token}
        )
        response_json = response.json()
        new_access_token = response_json['access_token']
        new_refresh_token = response_json['refresh_token']
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(new_access_token, old_access_token)
        self.assertNotEqual(new_refresh_token, old_refresh_token)

    def test_07_guest_confirm(self):
        self.unconfirmed_auth_user_client.post(
            reverse('confirm'),
            data={'email': self.unconfirmed_test_user.email}
        )
        confirm_code = ConfirmCode.objects.create(
            user=self.unconfirmed_test_user, code=generate_confirm_code()
        ).code
        response = self.guest_client.post(
            reverse('confirm'),
            data={
                'confirm_code': confirm_code,
                'email': self.unconfirmed_test_user.email,
                'password': self.unconfirmed_test_user_password
            }
        )
        unconfirmed_test_user = User.objects.get(
            email=self.unconfirmed_test_user.email
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(unconfirmed_test_user.is_confirm, True)

    def test_08_guest_cant_confirm_with_incorrect_password(self):
        self.unconfirmed_auth_user_client.post(
            reverse('confirm'),
            data={'email': self.unconfirmed_test_user.email}
        )
        confirm_code = ConfirmCode.objects.create(
            user=self.unconfirmed_test_user, code=generate_confirm_code()
        ).code
        invalid_password_response = self.guest_client.post(
            reverse('confirm'),
            data={
                'confirm_code': confirm_code,
                'email': self.unconfirmed_test_user.email,
                'password': '123456789$'
            }
        )
        less_them_8digit_password_response = self.guest_client.post(
            reverse('confirm'),
            data={
                'confirm_code': confirm_code,
                'email': self.unconfirmed_test_user.email,
                'password': '1234567'
            }
        )
        self.assertEqual(invalid_password_response.status_code, 403)
        self.assertEqual(less_them_8digit_password_response.status_code, 400)
