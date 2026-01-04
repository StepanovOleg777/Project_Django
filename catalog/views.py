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

# Импорты для кеширования
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings

from .models import Product, Category, Contact
from .forms import ProductForm


def home(request):
    """
    Контроллер для главной страницы.
    """
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


@cache_page(900)
def product_detail(request, pk):
    """
    Контроллер для отображения детальной информации о продукте.
    """
    product = get_object_or_404(Product.objects.select_related('category', 'owner'), pk=pk)

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

        if self.request.user.is_authenticated:
            if self.request.user.has_perm('catalog.view_product'):
                return queryset.order_by('-created_at')
            else:
                return queryset.filter(
                    status='published',
                    is_published=True
                ) | queryset.filter(owner=self.request.user)
        else:
            return queryset.filter(
                status='published',
                is_published=True
            ).order_by('-created_at')


class CachedProductListView(ListView):
    """
    Контроллер для отображения списка продуктов с низкоуровневым кешированием.
    """
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        if not settings.CACHE_ENABLED:
            return self.get_uncached_queryset()

        cache_key = 'product_list'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        queryset = self.get_uncached_queryset()
        cache.set(cache_key, queryset, 300)

        return queryset

    def get_uncached_queryset(self):
        queryset = Product.objects.select_related('category', 'owner')

        if self.request.user.is_authenticated:
            if self.request.user.has_perm('catalog.view_product'):
                return queryset.order_by('-created_at')
            else:
                return queryset.filter(
                    status='published',
                    is_published=True
                ) | queryset.filter(owner=self.request.user)
        else:
            return queryset.filter(
                status='published',
                is_published=True
            ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cache_enabled'] = settings.CACHE_ENABLED
        context['is_cached_view'] = True
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    Контроллер для создания нового продукта.
    """
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user

        if self.request.user.has_perm('catalog.change_product'):
            form.instance.status = 'moderation'

        if settings.CACHE_ENABLED:
            cache.delete('product_list')

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
        if settings.CACHE_ENABLED:
            cache.delete(f'product_detail_{self.object.pk}')
            cache.delete('product_list')

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
        product = self.get_object()

        if settings.CACHE_ENABLED:
            cache.delete(f'product_detail_{product.pk}')
            cache.delete('product_list')

        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Товар успешно удален!')
        return response


@login_required
@permission_required('catalog.can_unpublish_product', raise_exception=True)
def unpublish_product(request, pk):
    """
    Контроллер для снятия продукта с публикации.
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.is_published = False
        product.status = 'draft'
        product.save()

        if settings.CACHE_ENABLED:
            cache.delete(f'product_detail_{product.pk}')
            cache.delete('product_list')

        messages.success(request, f'Товар "{product.name}" снят с публикации.')
        return redirect('catalog:product_detail', pk=product.pk)

    context = {'product': product}
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

    if settings.CACHE_ENABLED:
        cache.delete(f'product_detail_{product.pk}')
        cache.delete('product_list')

    return redirect('catalog:product_detail', pk=pk)


def get_products_by_category(category_id):
    """
    Сервисная функция для получения всех продуктов в указанной категории.
    """
    return Product.objects.filter(
        category_id=category_id,
        status='published',
        is_published=True
    ).select_related('owner').order_by('-created_at')


def category_products(request, category_id):
    """
    Представление для отображения продуктов в указанной категории.
    """
    category = get_object_or_404(Category, id=category_id)

    products = get_products_by_category(category_id)

    context = {
        'category': category,
        'products': products,
        'title': f'Товары в категории: {category.name}',
    }

    return render(request, 'catalog/category_products.html', context)


@cache_page(60 * 15)
def test_cache_view(request):
    """
    Тестовая страница для проверки работы кеширования Redis.
    """
    import time

    current_time = time.time()

    context = {
        'current_time': current_time,
        'cache_enabled': settings.CACHE_ENABLED,
        'cache_timeout': 15,
    }

    return render(request, 'catalog/test_cache.html', context)