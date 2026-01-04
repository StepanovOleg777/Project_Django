# config/redis_utils.py
"""
Утилиты для работы с Redis.
"""

from django.conf import settings


def check_redis_connection():
    """
    Проверяет подключение к Redis.
    """
    if not settings.CACHE_ENABLED:
        return False, "Кеширование отключено (CACHE_ENABLED=False)"

    try:
        from django.core.cache import cache
        # Пробуем записать и прочитать тестовое значение
        test_key = 'redis_test_connection'
        test_value = 'test_value'

        cache.set(test_key, test_value, timeout=10)
        retrieved_value = cache.get(test_key)

        if retrieved_value == test_value:
            return True, "Redis подключен и работает"
        else:
            return False, "Ошибка чтения данных из Redis"

    except Exception as e:
        return False, f"Ошибка подключения: {str(e)}"


def get_cache_info():
    """
    Возвращает информацию о настройках кеширования.
    """
    return {
        'cache_enabled': settings.CACHE_ENABLED,
        'redis_host': settings.REDIS_HOST,
        'redis_port': settings.REDIS_PORT,
        'redis_db': settings.REDIS_DB,
    }