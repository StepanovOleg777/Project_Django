import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Загружает тестовые данные из фикстур в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все существующие данные перед загрузкой',
        )

    def handle(self, *args, **options):
        clear_data = options['clear']

        self.stdout.write('Начало загрузки тестовых данных...')

        if clear_data:
            self.stdout.write('Очистка существующих данных...')
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Существующие данные удалены')
            )

        # Загружаем фикстуры
        fixture_dir = os.path.join('catalog', 'fixtures')

        try:
            # Загружаем категории
            self.stdout.write('Загрузка категорий...')
            call_command('loaddata', 'category_data.json', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('Категории успешно загружены')
            )

            # Загружаем продукты
            self.stdout.write('Загрузка продуктов...')
            call_command('loaddata', 'product_data.json', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('Продукты успешно загружены')
            )

            # Выводим итоговую статистику
            categories_count = Category.objects.count()
            products_count = Product.objects.count()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Загрузка завершена! '
                    f'Загружено {categories_count} категорий и {products_count} продуктов'
                )
            )

            # Показываем примеры загруженных данных
            self.stdout.write('\nПримеры загруженных данных:')
            self.stdout.write('Категории:')
            for category in Category.objects.all()[:3]:
                products_count = category.products.count()
                self.stdout.write(f'  - {category.name} ({products_count} продуктов)')

            self.stdout.write('Продукты:')
            for product in Product.objects.all()[:3]:
                self.stdout.write(f'  - {product.name} - {product.price} руб.')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке данных: {str(e)}')
            )