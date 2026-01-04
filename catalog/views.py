# catalog/views.py
"""
Представления для приложения catalog.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

# Импорты для кеширования (задания 2, 4)
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings

from .models import Product, Category, Contact
from .forms import ProductForm


def home(request):
    """
    Контроллер для главной страницы.
    """
    # Получаем 6 последних опубликованных продуктов
    published_products = Product.objects.filter(
        status='published',
        is_published=True
    ).select_related('category', 'owner').order_by('-created_at')[:6]

    context = {
        'title': 'Главная - Интернет-магазин',
        'products': published_products,
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    """
    Контроллер для страницы контактов.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Сохраняем контакт в БД
        Contact.objects.create(
            name=name,
            phone=phone,
            message=message
        )

        messages.success(request, 'Сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
        return redirect('catalog:contacts')

    context = {
        'title': 'Контакты',
    }
    return render(request, 'catalog/contacts.html', context)


@cache_page(900)  # Кеширование на 15 минут (900 секунд) - ЗАДАНИЕ 2
def product_detail(request, pk):
    """
    Контроллер для отображения детальной информации о продукте.
    С кешированием через декоратор (задание 2).
    """
    product = get_object_or_404(Product.objects.select_related('category', 'owner'), pk=pk)

    # Проверяем права на просмотр
    if product.status != 'published' and not product.is_published:
        if not request.user.is_authenticated:
            raise PermissionDenied("Требуется авторизация для просмотра этого товара")
        if not (request.user == product.owner or
                request.user.has_perm('catalog.view_product') or
                request.user.has_perm('catalog.can_moderate_product')):
            raise PermissionDenied("У вас нет прав для просмотра этого товара")

    context = {
        'product': product,
        'can_edit': (
                request.user.is_authenticated and
                (request.user == product.owner or
                 request.user.has_perm('catalog.change_product'))
        ),
        'can_delete': (
                request.user.is_authenticated and
                (request.user == product.owner or
                 request.user.has_perm('catalog.delete_product'))
        ),
        'can_unpublish': (
                request.user.is_authenticated and
                request.user.has_perm('catalog.can_unpublish_product') and
                product.is_published
        ),
    }

    return render(request, 'catalog/product_detail.html', context)


class ProductListView(ListView):
    """
    Контроллер для отображения списка продуктов.
    """
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'owner')

        # Фильтрация по статусу для разных пользователей
        if self.request.user.is_authenticated:
            if self.request.user.has_perm('catalog.view_product'):
                # Модераторы видят все продукты
                return queryset.order_by('-created_at')
            else:
                # Обычные пользователи видят опубликованные и свои продукты
                return queryset.filter(
                    status='published',
                    is_published=True
                ) | queryset.filter(owner=self.request.user)
        else:
            # Неавторизованные видят только опубликованные
            return queryset.filter(
                status='published',
                is_published=True
            ).order_by('-created_at')


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    Контроллер для создания нового продукта.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def form_valid(self, form):
        # Устанавливаем текущего пользователя как владельца
        form.instance.owner = self.request.user

        # Если пользователь имеет право на публикацию, можно сразу публиковать
        if self.request.user.has_perm('catalog.change_product'):
            form.instance.status = 'moderation'

        messages.success(self.request, 'Товар успешно создан!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Контроллер для редактирования продукта.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def test_func(self):
        product = self.get_object()
        return (self.request.user == product.owner or
                self.request.user.has_perm('catalog.change_product'))

    def form_valid(self, form):
        # Сбрасываем кеш этого продукта при обновлении - ЗАДАНИЕ 2
        if settings.CACHE_ENABLED:
            cache_key = f'product_detail_{self.object.pk}'
            cache.delete(cache_key)

        messages.success(self.request, 'Товар успешно обновлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Контроллер для удаления продукта.
    """
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')

    def test_func(self):
        product = self.get_object()
        return (self.request.user == product.owner or
                self.request.user.has_perm('catalog.delete_product'))

    def delete(self, request, *args, **kwargs):
        # Получаем продукт перед удалением
        product = self.get_object()

        # Сбрасываем кеш этого продукта при удалении - ЗАДАНИЕ 2
        if settings.CACHE_ENABLED:
            cache_key = f'product_detail_{product.pk}'
            cache.delete(cache_key)

        # Удаляем продукт
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Товар успешно удален!')
        return response


@login_required
@permission_required('catalog.can_unpublish_product', raise_exception=True)
def unpublish_product(request, pk):
    """
    Контроллер для снятия продукта с публикации.
    Доступно только пользователям с правом can_unpublish_product.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.is_published = False
        product.status = 'draft'
        product.save()

        # Сбрасываем кеш этого продукта - ЗАДАНИЕ 2
        if settings.CACHE_ENABLED:
            cache_key = f'product_detail_{product.pk}'
            cache.delete(cache_key)

        messages.success(request, f'Товар "{product.name}" снят с публикации.')
        return redirect('catalog:product_detail', pk=product.pk)

    context = {
        'product': product,
    }
    return render(request, 'catalog/product_unpublish.html', context)


@login_required
@permission_required('catalog.can_moderate_product', raise_exception=True)
def moderate_product(request, pk, action):
    """
    Контроллер для модерации продукта.
    """
    product = get_object_or_404(Product, pk=pk)

    if action == 'approve':
        product.status = 'published'
        product.is_published = True
        messages.success(request, f'Товар "{product.name}" одобрен и опубликован.')
    elif action == 'reject':
        product.status = 'rejected'
        product.is_published = False
        messages.warning(request, f'Товар "{product.name}" отклонен.')
    else:
        messages.error(request, 'Неверное действие модерации.')
        return redirect('catalog:product_detail', pk=pk)

    product.save()

    # Сбрасываем кеш этого продукта - ЗАДАНИЕ 2
    if settings.CACHE_ENABLED:
        cache_key = f'product_detail_{product.pk}'
        cache.delete(cache_key)

    return redirect('catalog:product_detail', pk=pk)


# ================ ЗАДАНИЕ 1: Тестовая страница для проверки Redis ================

@cache_page(60 * 15)  # Кешируем на 15 минут
def test_cache_view(request):
    """
    Тестовая страница для проверки работы кеширования Redis.
    Используется в задании 1.
    """
    import time

    # Генерируем текущее время
    current_time = time.time()

    context = {
        'current_time': current_time,
        'cache_enabled': settings.CACHE_ENABLED,
        'cache_timeout': 15,  # минут
    }

    return render(request, 'catalog/test_cache.html', context)


# ================ ЗАДАНИЕ 3: Сервисная функция и представление для категорий ================

def get_products_by_category(category_id):
    """
    Сервисная функция для получения всех продуктов в указанной категории.
    Используется в задании 3.

    Args:
        category_id: ID категории

    Returns:
        QuerySet: Продукты в указанной категории
    """
    return Product.objects.filter(
        category_id=category_id,
        status='published',
        is_published=True
    ).select_related('owner').order_by('-created_at')


def category_products(request, category_id):
    """
    Представление для отображения продуктов в указанной категории.
    Используется в задании 3.
    """
    category = get_object_or_404(Category, id=category_id)

    # Используем сервисную функцию для получения продуктов
    products = get_products_by_category(category_id)

    context = {
        'category': category,
        'products': products,
        'title': f'Товары в категории: {category.name}',
    }

    return render(request, 'catalog/category_products.html', context)


# ================ ЗАДАНИЕ 4: Низкоуровневое кеширование списка продуктов ================

class CachedProductListView(ListView):
    """
    Контроллер для отображения списка продуктов с низкоуровневым кешированием.
    Используется в задании 4.
    """
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        # Проверяем, включено ли кеширование
        if not settings.CACHE_ENABLED:
            return self.get_uncached_queryset()

        # Создаем уникальный ключ для кеша
        cache_key = 'product_list'

        # Пробуем получить данные из кеша
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            # Данные есть в кеше - возвращаем их
            return cached_data

        # Данных нет в кеше - получаем свежие данные
        queryset = self.get_uncached_queryset()

        # Сохраняем в кеш на 5 минут (300 секунд)
        cache.set(cache_key, queryset, 300)

        return queryset

    def get_uncached_queryset(self):
        """
        Получение QuerySet без кеширования.
        """
        queryset = Product.objects.select_related('category', 'owner')

        # Фильтрация по статусу для разных пользователей
        if self.request.user.is_authenticated:
            if self.request.user.has_perm('catalog.view_product'):
                # Модераторы видят все продукты
                return queryset.order_by('-created_at')
            else:
                # Обычные пользователи видят опубликованные и свои продукты
                return queryset.filter(
                    status='published',
                    is_published=True
                ) | queryset.filter(owner=self.request.user)
        else:
            # Неавторизованные видят только опубликованные
            return queryset.filter(
                status='published',
                is_published=True
            ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию о кешировании в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['cache_enabled'] = settings.CACHE_ENABLED
        context['is_cached_view'] = True
        return context