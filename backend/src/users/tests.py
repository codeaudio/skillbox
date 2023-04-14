from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from test_utils.auth import client_auth

User = get_user_model()


class TestUser(APITestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User(
            username='test1',
            email='test1@mail.ru',
            is_active=1,
            is_confirm=1
        )
        cls.test_user_password = '1234578'
        cls.test_user.set_password(cls.test_user_password)
        cls.test_user.save()
        cls.auth_user_client = cls.client_class()
        cls.guest_client = cls.client_class()
        cls.admin_user = User(
            username='admin',
            email='admin@mail.ru',
            is_active=1,
            is_confirm=1,
            is_superuser=1
        )
        cls.admin_user_password = 'qwerty'
        cls.admin_user.set_password(cls.admin_user_password)
        cls.admin_user.save()
        cls.admin_client = cls.client_class()
        client_auth(
            client=cls.admin_client,
            username=cls.admin_user.username,
            email=cls.admin_user.email,
        )
        client_auth(
            client=cls.auth_user_client,
            username=cls.test_user.username,
            email=cls.test_user.email,
        )
        super().setUpTestData()

    def test_01_guest_registration(self):
        email = 'test5@ya.ru'
        response = self.guest_client.post(
            reverse('user_registration'),
            data={
                "username": "testfsd",
                "password": "12345678",
                "email": email
            }
        )
        is_user = User.objects.filter(email=email).exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_user, True)

    def test_02_auth_user_cant_registration(self):
        email = 'test5@ya.ru'
        response = self.auth_user_client.post(
            reverse('user_registration'),
            data={
                "username": "testfsd",
                "password": "12345678",
                "email": email
            }
        )
        is_user = User.objects.filter(email=email).exists()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(is_user, False)

    def test_03_guest_registration_with_no_latin_username(self):
        email = 'test5@ya.ru'
        username = 'юзер'
        response = self.guest_client.post(
            reverse('user_registration'),
            data={
                "username": username,
                "password": "12345678",
                "email": email
            }
        )
        is_user = User.objects.filter(email=email).exists()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(is_user, False)

    def test_04_guest_registration_with_incorrect_email(self):
        email = 'test5ya.ru'
        response = self.guest_client.post(
            reverse('user_registration'),
            data={
                "username": 'testtest',
                "password": "12345678",
                "email": email
            }
        )
        is_user = User.objects.filter(email=email).exists()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(is_user, False)

    def test_05_guest_registration_with_incorrect_password(self):
        email = 'test5ya.ru'
        response = self.guest_client.post(
            reverse('user_registration'),
            data={
                "username": 'testtest',
                "password": "12",
                "email": 'test5@ya.ru'
            }
        )
        is_user = User.objects.filter(email=email).exists()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(is_user, False)

    def test_06_guest_cant_get_users(self):
        response = self.guest_client.get(reverse('users'))
        self.assertEqual(response.status_code, 403)

    def test_07_auth_user_cant_get_users(self):
        response = self.auth_user_client.get(reverse('users'))
        self.assertEqual(response.status_code, 403)

    def test_08_admin_get_users(self):
        response = self.admin_client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['results']), 0)

    def test_09_user_get_self(self):
        response = self.auth_user_client.get(
            reverse('user', kwargs={'username': self.test_user.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_09_user_cant_get_another_user(self):
        response = self.auth_user_client.get(
            reverse('user', kwargs={'username': self.admin_user.username})
        )
        self.assertEqual(response.status_code, 403)

    def test_10_admin_get_another_user(self):
        response = self.admin_client.get(
            reverse('user', kwargs={'username': self.test_user.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
