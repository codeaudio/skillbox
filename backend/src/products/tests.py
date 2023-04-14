import os

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from products.models import Cart, Group, Order, Product
from test_utils.auth import client_auth

User = get_user_model()


class TestProduct(APITestCase):
    client_class = APIClient
    product_csv_file_path = (
        f'{os.path.dirname(__file__)}/../test_utils/products.csv'
    )
    group_csv_file_path = (
        f'{os.path.dirname(__file__)}/../test_utils/groups.csv'
    )

    def import_products_csv(self):
        with open(self.product_csv_file_path) as f:
            return self.admin_client.post(
                reverse('import_products'),
                data=f.read(),
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachement; filename=product',
                }
            )

    def import_groups_csv(self):
        with open(self.group_csv_file_path) as f:
            return self.admin_client.post(
                reverse('import_groups'),
                data=f.read(),
                content_type='text/csv',
                headers={
                    'Content-Disposition': 'attachement; filename=group',
                }
            )

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

        cls.auth_user_client = cls.client_class()
        cls.guest_client = cls.client_class()
        cls.admin_client = cls.client_class()
        client_auth(
            client=cls.auth_user_client,
            username=cls.test_user.username,
            email=cls.test_user.email,
        )
        client_auth(
            client=cls.admin_client,
            username=cls.admin_user.username,
            email=cls.admin_user.email,
        )
        super().setUpTestData()

    def test_01_guest_cant_import_products(self):
        response = self.guest_client.post(
            reverse('import_products')
        )
        self.assertEqual(response.status_code, 403)

    def test_02_auth_user_cant_import_products(self):
        response = self.auth_user_client.post(
            reverse('import_products')
        )
        self.assertEqual(response.status_code, 403)

    def test_03_admin_user_import_products_without_file(self):
        response = self.admin_client.post(
            reverse('import_products')
        )
        self.assertEqual(response.status_code, 400)

    def test_04_admin_user_import_products_with_incorrect_file(self):
        response = self.admin_client.post(
            reverse('import_products'),
            data={'file': ''},
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachement; filename=products'
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_05_guest_cant_import_groups(self):
        response = self.guest_client.post(
            reverse('import_groups')
        )
        self.assertEqual(response.status_code, 403)

    def test_06_auth_user_cant_import_groups(self):
        response = self.auth_user_client.post(
            reverse('import_groups')
        )
        self.assertEqual(response.status_code, 403)

    def test_07_admin_user_import_groups_without_file(self):
        response = self.admin_client.post(
            reverse('import_groups')
        )
        self.assertEqual(response.status_code, 400)

    def test_08_admin_user_import_groups_with_incorrect_file(self):
        response = self.admin_client.post(
            reverse('import_groups'),
            data={'file': ''},
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachement; filename=groups'
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_09_admin_user_import_groups_with_correct_file(self):
        is_product_before = Group.objects.all().exists()
        response = self.import_groups_csv()
        is_product_after = Group.objects.all().exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_product_before, False)
        self.assertEqual(is_product_after, True)

    def test_10_admin_user_import_products_with_correct_file(self):
        self.import_groups_csv()

        is_product_before = Product.objects.all().exists()
        response = self.import_products_csv()
        is_product_after = Product.objects.all().exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_product_before, False)
        self.assertEqual(is_product_after, True)

    def test_11_guest_can_get_products_list(self):
        self.import_groups_csv()
        self.import_products_csv()
        response = self.admin_client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['results']), 0)

    def test_12_auth_user_can_get_products_list(self):
        self.import_groups_csv()
        self.import_products_csv()
        response = self.auth_user_client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['results']), 0)

    def test_13_admin_can_get_products_list(self):
        self.import_groups_csv()
        self.import_products_csv()
        response = self.admin_client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['results']), 0)

    def test_14_guest_can_get_product_retrieve(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.guest_client.get(reverse('product', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_15_auth_user_can_get_product_retrieve(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.auth_user_client.get(
            reverse('product', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_16_admin_can_get_product_retrieve(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.admin_client.get(reverse('product', kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

    def test_17_guest_cant_add_to_cart(self):
        response = self.guest_client.post(
            reverse('add_to_cart', kwargs={'pk': 1})
        )
        self.assertEqual(response.status_code, 403)

    def test_18_auth_user_add_to_cart(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.auth_user_client.post(
            reverse('add_to_cart', kwargs={'pk': pk}),
            data={'amount': 1}
        )
        is_cart = Cart.objects.filter(user_id=self.test_user.pk).exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_cart, True)

    def test_19_admin_add_to_cart(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.admin_client.post(
            reverse('add_to_cart', kwargs={'pk': pk}),
            data={'amount': 1}
        )
        is_cart = Cart.objects.filter(user_id=self.admin_user.pk).exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_cart, True)

    def test_20_cant_add_to_cart_if_amount_greeter_then_product_amount(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        response = self.auth_user_client.post(
            reverse('add_to_cart', kwargs={'pk': pk}),
            data={'amount': 999999999999999999999999999999999999999999}
        )
        is_cart = Cart.objects.filter(user_id=self.test_user.pk).exists()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(is_cart, False)

    def test_21_guest_user_cant_create_order(self):
        response = self.guest_client.post(reverse('create_order'))
        self.assertEqual(response.status_code, 403)

    def test_22_auth_user_can_create_order(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        self.auth_user_client.post(
            reverse('add_to_cart', kwargs={'pk': pk}),
            data={'amount': 1}
        )
        response = self.auth_user_client.post(reverse('create_order'))
        is_order = Order.objects.filter(user_id=self.test_user.pk).exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_order, True)

    def test_23_admin_can_create_order(self):
        self.import_groups_csv()
        self.import_products_csv()
        pk = Product.objects.first().pk
        self.admin_client.post(
            reverse('add_to_cart', kwargs={'pk': pk}),
            data={'amount': 1}
        )
        response = self.admin_client.post(reverse('create_order'))
        is_order = Order.objects.filter(user_id=self.admin_user.pk).exists()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(is_order, True)
