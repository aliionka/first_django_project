from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена") # DecimalField - для денег, точнее считает
    description = models.TextField(max_length=100, blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    discount_range = models.PositiveSmallIntegerField(verbose_name="Диапазон скидки")
    promotion_start_date = models.DateTimeField(verbose_name="Дата начала акции")
    promotion_end_date = models.DateTimeField(verbose_name="Дата окончания акции")
    stock_availability = models.BooleanField(verbose_name="Наличие на складе")

    def __str__(self):
        return self.name


class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    products = models.ManyToManyField(Product, verbose_name="Товары")
    address = models.CharField(max_length=50, verbose_name="Адрес доставки")
    comment = models.TextField(max_length=100, verbose_name="Комментарий", default="", blank=True)

    def __str__(self):
        return f"Заказ №{self.id} от {self.user.username}"