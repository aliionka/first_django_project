from django.core.management.base import BaseCommand
from shopapp.models import Product
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create sample products using get_or_create'

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')

        # Список продуктов для создания
        products_data = [
            {
                'name': 'Ноутбук Dell XPS 13',
                'price': 1500.00,
                'description': 'Мощный ноутбук для работы и игр',
                'discount_range': 10,
                'promotion_start_date': datetime.now(),
                'promotion_end_date': datetime.now() + timedelta(days=30),
                'stock_availability': True,
            },
            {
                'name': 'iPhone 15 Pro',
                'price': 1200.00,
                'description': 'Смартфон последнего поколения',
                'discount_range': 5,
                'promotion_start_date': datetime.now(),
                'promotion_end_date': datetime.now() + timedelta(days=15),
                'stock_availability': True,
            },
            {
                'name': 'Наушники Sony WH-1000XM5',
                'price': 350.00,
                'description': 'Беспроводные наушники с шумоподавлением',
                'discount_range': 15,
                'promotion_start_date': datetime.now(),
                'promotion_end_date': datetime.now() + timedelta(days=45),
                'stock_availability': True,
            },
            {
                'name': 'Клавиатура Logitech MX Keys',
                'price': 120.00,
                'description': 'Эргономичная беспроводная клавиатура',
                'discount_range': 8,
                'promotion_start_date': datetime.now(),
                'promotion_end_date': datetime.now() + timedelta(days=20),
                'stock_availability': False,
            },
            {
                'name': 'Монитор LG 27" 4K',
                'price': 450.00,
                'description': 'Профессиональный монитор для дизайнеров',
                'discount_range': 12,
                'promotion_start_date': datetime.now(),
                'promotion_end_date': datetime.now() + timedelta(days=60),
                'stock_availability': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for product_data in products_data:
            # Используем get_or_create (название товара должно быть уникальным)
            obj, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'price': product_data['price'],
                    'description': product_data['description'],
                    'discount_range': product_data['discount_range'],
                    'promotion_start_date': product_data['promotion_start_date'],
                    'promotion_end_date': product_data['promotion_end_date'],
                    'stock_availability': product_data['stock_availability'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {obj.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Product already exists: {obj.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} products, {updated_count} already existed'
        ))