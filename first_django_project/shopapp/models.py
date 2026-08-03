from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User


class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    name = models.CharField(
        max_length=30,
        verbose_name="Название товара"
    )
    price = models.DecimalField( # DecimalField - для денег, точнее считает
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    description = models.TextField(
        max_length=100,
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    discount = models.PositiveSmallIntegerField(
        verbose_name="Скидка",
        default=0)
    promotion_start_date = models.DateTimeField(
        verbose_name="Дата начала акции",
        null=True,
        blank=True
    )
    promotion_end_date = models.DateTimeField(
        verbose_name="Дата окончания акции",
        null=True,
        blank=True
    )
    stock_availability = models.BooleanField(
        verbose_name="Наличие на складе",
        default=False
    )
    archived = models.BooleanField(
        default=False,
        verbose_name="Архивирован"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT, # запрещает удаление пользователя,если у него есть продукты
        related_name="products", # можно писать user.products.all()
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )

    # @property
    # def description_short(self) -> str:
    #     if len(self.description) < 48:
    #         return self.description
    #     return self.description[:48] + "..."

    def __str__(self):
        return f"{self.name!r}, цена: {self.price}"


class Order(models.Model):
    order_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата заказа"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    products = models.ManyToManyField(
        Product,
        verbose_name="Товары",
        related_name="orders"
    )
    address = models.CharField(
        max_length=50,
        verbose_name="Адрес доставки"
    )
    comment = models.TextField(
        max_length=100,
        verbose_name="Комментарий",
        default="",
        blank=True
    )

    def __str__(self):
        return f"Заказ №{self.id} от {self.user.username}"
