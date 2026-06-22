from django.core.management.base import BaseCommand
from shopapp.models import Order, Product
from django.contrib.auth.models import User
from datetime import datetime
import random


class Command(BaseCommand):
    help = 'Create sample orders using get_or_create'

    def handle(self, *args, **options):
        self.stdout.write('Creating orders...')

        # Проверяем, есть ли пользователи
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found! Please create a user first.'))
            return

        # Проверяем, есть ли продукты
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(self.style.ERROR('No products found! Please run create_products first.'))
            return

        # Данные для заказов
        orders_data = [
            {
                'address': 'Москва, ул. Тверская, д. 1',
                'comment': 'Доставить до 18:00',
                'user': users[0],  # Первый пользователь
                'products': [products[0], products[1]],  # Ноутбук и iPhone
            },
            {
                'address': 'Санкт-Петербург, Невский проспект, д. 10',
                'comment': 'Позвонить перед доставкой',
                'user': users[0] if len(users) > 0 else users[0],
                'products': [products[2], products[3]],  # Наушники и клавиатура
            },
            {
                'address': 'Новосибирск, ул. Ленина, д. 5',
                'comment': 'Оставьте у двери',
                'user': users[0] if len(users) > 0 else users[0],
                'products': [products[0], products[2], products[4]],  # Ноутбук, наушники, монитор
            },
        ]

        created_count = 0
        existing_count = 0

        for order_data in orders_data:
            # Используем get_or_create (используем уникальную комбинацию полей)
            # Так как нет уникального поля, используем дату + пользователя + адрес
            order, created = Order.objects.get_or_create(
                user=order_data['user'],
                address=order_data['address'],
                defaults={
                    'order_date': datetime.now(),
                    'comment': order_data['comment'],
                }
            )

            if created:
                # Добавляем продукты в заказ
                order.products.set(order_data['products'])
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created order #{order.id} for {order.user.username}'
                ))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(
                    f'Order already exists: #{order.id} for {order.user.username}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} orders, {existing_count} already existed'
        ))