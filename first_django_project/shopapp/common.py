import csv
from csv import DictReader
from django.contrib.auth.models import User
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    """Импорт заказов из CSV-файла"""
    file = TextIOWrapper(file, encoding=encoding)

    reader = csv.DictReader(file, delimiter=",", quotechar='"')
    orders = []

    for row in reader:
        try:
            # Находим пользователя по username
            user = User.objects.get(username=row["user"])
        except User.DoesNotExists:
            # Если пользователя нет — пропускаем
            continue

        # Находим продукты по именам
        product_names = [name.strip() for name in row["products"].split(",")]
        products = Product.objects.filter(name__in=product_names)

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            address=row["address"],
            promocode=row.get("promocode", ""),
        )
        order.products.set(products)
        orders.append(order)
    return orders


