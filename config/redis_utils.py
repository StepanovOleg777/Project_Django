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


def clear_product_cache(product_id=None):
    """
    Очищает кеш для продукта(ов).

    Args:
        product_id: ID продукта или None для очистки всех продуктов
    """
    if not settings.CACHE_ENABLED:
        return 0

    try:
        from django.core.cache import cache

        if product_id:
            # Очищаем кеш конкретного продукта
            cache_key = f'product_detail_{product_id}'
            if hasattr(cache, 'delete_pattern'):
                # Для django-redis
                return cache.delete_pattern(f'{cache_key}_*')
            else:
                # Для стандартного кеша
                cache.delete(cache_key)
                return 1
        else:
            # Очищаем кеш всех продуктов
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern('product_detail_*')
            else:
                # Для стандартного кеша нужно знать все ключи
                return 0
    except Exception as e:
        print(f"Ошибка при очистке кеша: {e}")
        return 0