# catalog/management/commands/clear_product_list_cache.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Очищает кеш списка продуктов'

    def handle(self, *args, **options):
        if not settings.CACHE_ENABLED:
            self.stdout.write(self.style.WARNING('Кеширование отключено (CACHE_ENABLED=False)'))
            return

        cache_key = 'product_list'
        deleted = cache.delete(cache_key)

        if deleted:
            self.stdout.write(self.style.SUCCESS(f'Кеш списка продуктов очищен (ключ: {cache_key})'))
        else:
            self.stdout.write(self.style.WARNING(f'Кеш списка продуктов не найден (ключ: {cache_key})'))