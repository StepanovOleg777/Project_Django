# catalog/management/commands/clear_product_cache.py
"""
Команда для очистки кеша продуктов.
"""

from django.core.management.base import BaseCommand
from config.redis_utils import clear_product_cache


class Command(BaseCommand):
    help = 'Очищает кеш продуктов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='ID конкретного продукта для очистки кеша',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Очистить кеш всех продуктов',
        )

    def handle(self, *args, **options):
        product_id = options.get('product_id')
        clear_all = options.get('all')

        self.stdout.write("Очистка кеша продуктов...")

        if product_id:
            cleared = clear_product_cache(product_id)
            self.stdout.write(self.style.SUCCESS(
                f"Кеш продукта {product_id} очищен. Удалено ключей: {cleared}"
            ))
        elif clear_all:
            cleared = clear_product_cache()
            self.stdout.write(self.style.SUCCESS(
                f"Кеш всех продуктов очищен. Удалено ключей: {cleared}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Укажите --product-id <id> для очистки кеша конкретного продукта "
                "или --all для очистки всех продуктов"
            ))