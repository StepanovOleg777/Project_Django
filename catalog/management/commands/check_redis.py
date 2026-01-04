# catalog/management/commands/check_redis.py
"""
Команда для проверки подключения Redis.
"""

from django.core.management.base import BaseCommand
from config.redis_utils import check_redis_connection, get_cache_info


class Command(BaseCommand):
    help = 'Проверяет настройки Redis и подключение'

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Проверка настроек Redis")
        self.stdout.write("=" * 50)

        # Показываем настройки
        info = get_cache_info()

        self.stdout.write(f"\nНастройки кеширования:")
        self.stdout.write(f"  CACHE_ENABLED: {info['cache_enabled']}")
        self.stdout.write(f"  Redis хоcт: {info['redis_host']}")
        self.stdout.write(f"  Redis порт: {info['redis_port']}")
        self.stdout.write(f"  Redis БД: {info['redis_db']}")

        # Проверяем подключение
        if info['cache_enabled']:
            self.stdout.write("\nПроверка подключения к Redis...")
            success, message = check_redis_connection()

            if success:
                self.stdout.write(self.style.SUCCESS(f"✓ {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {message}"))
        else:
            self.stdout.write(self.style.WARNING(
                "\nКеширование отключено. Для включения установите CACHE_ENABLED=True в .env"
            ))

        self.stdout.write("\n" + "=" * 50)