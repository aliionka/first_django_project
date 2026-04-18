from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми товарами'

    def handle(self, *args, **options):
        # Очищаем старые данные
        Product.objects.all().delete()
        self.stdout.write('Старые товары удалены')

        # Создаем новые товары
        products_data = [
            ('Laptop', 2999.00, 'Мощный ноутбук для работы и игр'),
            ('Headphones', 999.00, 'Беспроводные наушники с шумоподавлением'),
            ('Smartphone', 1500.00, 'Смартфон с отличной камерой'),
            ('Joystick', 1000.00, 'Геймпад для компьютера'),
            ('Keyboard', 2500.00, 'Механическая клавиатура с подсветкой'),
            ('Mouse', 500.00, 'Игровая мышь'),
        ]

        for name, price, description in products_data:
            product = Product.objects.create(
                name=name,
                price=price,
                description=description
            )
            self.stdout.write(f'✅ Добавлен товар: {product.name} - ${product.price}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Успешно добавлено {len(products_data)} товаров!'))