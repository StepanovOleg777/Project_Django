from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()  # Получаем вашу кастомную модель User


class Category(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Наименование',
        help_text='Введите наименование категории'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Введите описание категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель продукта/товара
    """
    # Основные поля
    name = models.CharField(
        max_length=100,
        verbose_name='Наименование',
        help_text='Введите наименование продукта'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Введите описание продукта'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
        blank=True,
        null=True,
        help_text='Загрузите изображение продукта'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='products',
        help_text='Выберите категорию продукта'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за покупку',
        help_text='Введите цену продукта'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего изменения'
    )

    # === ЗАДАНИЕ 2: Добавляем поле владельца ===
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Владелец',
        related_name='products',
        help_text='Владелец продукта'
    )

    # === ЗАДАНИЕ 1: Добавляем поле статуса публикации ===
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус',
        help_text='Статус продукта'
    )

    # Поле для быстрой проверки публикации
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
        help_text='Продукт опубликован и виден всем пользователям'
    )

    # Дополнительные поля для модерации
    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата модерации'
    )
    moderator_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий модератора',
        help_text='Комментарий модератора по продукту'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

        # === ЗАДАНИЕ 1: Кастомные права ===
        permissions = [
            ('can_unpublish_product', 'Может отменять публикацию продукта'),
            ('can_change_category', 'Может изменять категорию продукта'),
            ('can_moderate_product', 'Может модерировать продукты'),
        ]

    def __str__(self):
        return f"{self.name} - {self.price} руб."

    def save(self, *args, **kwargs):
        """Автоматически обновляем is_published в зависимости от статуса"""
        if self.status == 'published':
            self.is_published = True
        else:
            self.is_published = False
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Модель для хранения контактных данных"""
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"