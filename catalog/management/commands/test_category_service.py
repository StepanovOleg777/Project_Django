# catalog/management/commands/test_category_service.py
from django.core.management.base import BaseCommand
from catalog.models import Category
from catalog.views import get_products_by_category


class Command(BaseCommand):
    help = 'Тестирует сервисную функцию get_products_by_category'

    def add_arguments(self, parser):
        parser.add_argument(
            'category_id',
            type=int,
            help='ID категории для тестирования'
        )

    def handle(self, *args, **options):
        category_id = options['category_id']

        try:
            category = Category.objects.get(id=category_id)
            self.stdout.write(f"Тестирование категории: {category.name}")

            # Используем сервисную функцию
            products = get_products_by_category(category_id)

            self.stdout.write(f"Найдено товаров: {products.count()}")

            for product in products[:5]:  # Покажем первые 5
                self.stdout.write(f"  - {product.name} ({product.price} ₽)")

            if products.count() > 5:
                self.stdout.write(f"  ... и еще {products.count() - 5} товаров")

        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Категория с ID {category_id} не найдена"))