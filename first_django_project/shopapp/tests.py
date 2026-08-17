from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.html import escape

from string import ascii_letters
from random import choices

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


# python manage.py test shopapp.tests.AddTwoNumbersTestCase - запускает класс AddTwoNumbersTestCase
# python manage.py test shopapp.tests - запускает все классы тестов

# python manage.py dumpdata shopapp.Product > shopapp-fixtures.json - выгрузка таблиц из приложения в файл
# ctrl + Alt + L - для форматирования json-файла в читаемый вид

class ProductCreateViewTestCase(TestCase):

    def setUp(self) -> None:
        # Создаем пользователя
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )

        # Даем права на создание продуктов
        content_type = ContentType.objects.get_for_model(Product)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="add_product"
        )
        self.user.user_permissions.add(permission)

        # Логиним пользователя
        self.client.login(username="testuser", password="testpassword")

        # Генерируем имя продукта
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:create_product"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table!",
                "stock_availability": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.product = Product.objects.create(
            name="Best product",
            price=99.99,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = ["products-fixtures.json"]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        # content = response.content.decode("utf-8")
        #
        # for product in Product.objects.filter(archived=False):
        #     # ссылка на продукт присутствует
        #     detail_url = reverse("shopapp:product_details", kwargs={"pk": product.pk})
        #     self.assertIn(detail_url, content)
        #
        #     # имя продукта есть (с экранированием)
        #     escaped_name = escape(product.name)
        #     self.assertIn(escaped_name, content)

        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )


class OrdersListViewTestCase(TestCase):
    fixtures = ["orders-fixtures.json"]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(id=1, username="bob_test", password="qwert")
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:order_list"))
        # self.assertContains(response, "Order")

        self.assertEqual(response.status_code, 200)
        orders = Order.objects.filter(user=self.user)
        for order in orders:
            # Проверяем, что адрес заказа отображается
            self.assertContains(response, order.address)

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username="tom_test", password="tom_test1")
        cls.user = User.objects.create_user(**cls.credentials)

        # разрешение на просмотр заказов
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="view_order"
        )
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.login(**self.credentials)
        self.order = Order.objects.create(
            user=self.user,
            address="Test address, 123",
            comment="No comment"
        )

    def tearDown(self):
        if hasattr(self, "order"):
            self.order.delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_order_details(self):
        # GET запрос к странице заказа
        response = self.client.get(
            reverse("shopapp:order_detail"), kwargs={"pk": self.order.pk}
        )
        self.assertEqual(response.status_code, 200)
        # Проверить, что адрес и промокод есть в теле ответа
        self.assertContains(response, self.order.address)
        self.assertContains(response, self.order.promocode)
        # Проверить, что в контексте правильный заказ (по pk)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "users-fixtures.json",
        "products-fixtures.json",
        "orders-fixtures.json"
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(pk=1)
        cls.credentials = dict(
            username=cls.user.username,
            password="Aiionka103ploTik"
        )
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="view_order"
        )
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.login(**self.credentials)

        self.order = Order.objects.get(pk=1)
        self.product1 = Product.objects.get(pk=1)
        self.product2 = Product.objects.get(pk=2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def tearDown(self):
        # if hasattr(self, "order"):
        #     self.order.delete()
        # if hasattr(self, "product1"):
        #     self.product1.delete()
        # if hasattr(self, "product2"):
        #     self.product2.delete()
        pass

    def test_get_list_orders(self):
        """Получение экспорта заказов"""
        response = self.client.get(reverse("shopapp:orders_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = response.json()
        self.assertIn("orders", data)
        self.assertIn("count", data)

        # Проверяем, что есть хотя бы один заказ
        self.assertGreater(data["count"], 0)

        # Находим наш заказ в списке
        order_data = None
        for order in data["orders"]:
            if order["pk"] == self.order.pk:
                order_data = order
                break

        # Проверяем, что заказ найден
        self.assertIsNotNone(order_data, f"Заказ #{self.order.pk} не найден в экспорте")

        self.assertEqual(order_data["address"], self.order.address)
        self.assertEqual(order_data["promocode"], self.order.promocode)
        self.assertEqual(order_data["user_id"], self.user.pk)
        self.assertEqual(order_data["user_name"], self.user.username)

        # Проверяем продукты
        expected_product_ids = [self.product1.pk, self.product2.pk]
        for product_id in expected_product_ids:
            self.assertIn(
                product_id,
                order_data["list_id_products"],
                f"Продукт {product_id} не найден в заказе"
            )

    def test_orders_export_filters_by_user(self):
        """Фильтрация заказов по пользователю"""
        user2 = User.objects.exclude(pk=self.user.pk).first()
        self.assertIsNotNone(user2, "В фикстуре должен быть другой пользователь")

        response = self.client.get(
            reverse("shopapp:orders_export") + f"?user_id={user2.pk}"
        )
        data = response.json()

        # Проверяем, что все заказы принадлежат user2
        for order in data["orders"]:
            self.assertEqual(order["user_id"], user2.pk)

    def test_orders_export_respects_limit(self):
        """Параметр limit работает корректно"""
        limit = 2
        response = self.client.get(
            reverse("shopapp:orders_export") + f"?limit={limit}"
        )
        data = response.json()
        # Проверяем, что количество не превышает limit
        self.assertLessEqual(data["count"], limit)


# python manage.py dumpdata auth.User --indent 2 > shopapp/fixtures/users-fixtures.json
# python manage.py dumpdata shopapp.Product --indent 2 > shopapp/fixtures/products-fixtures.json
# python manage.py dumpdata shopapp.Order --indent 2 > shopapp/fixtures/orders-fixtures.json
