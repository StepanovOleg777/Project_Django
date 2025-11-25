from django.db import models


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

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.price} руб."


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