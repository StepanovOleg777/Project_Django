from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm


def home(request):
    """Контроллер главной страницы"""
    # Показываем только опубликованные продукты
    products = Product.objects.filter(is_published=True)[:6]

    context = {
        'products': products,
        'title': 'Главная - Магазин'
    }
    return render(request, "catalog/home.html", context)


def contacts(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        return render(request, "catalog/contacts.html", {"success": True})
    return render(request, "catalog/contacts.html")


def product_detail(request, pk):
    """Контроллер для страницы одного товара"""
    # Разные правила доступа в зависимости от пользователя
    user = request.user

    if user.is_authenticated:
        # Авторизованные пользователи видят больше
        if user.is_superuser or user.groups.filter(name='Модератор продуктов').exists():
            # Админы и модераторы видят все продукты
            product = get_object_or_404(Product, pk=pk)
        elif user.groups.filter(name='Контент-менеджер').exists():
            # Контент-менеджеры видят все, кроме черновиков других пользователей
            product = get_object_or_404(
                Product.objects.exclude(status='draft', owner__isnull=False).exclude(
                    status='draft', owner=user
                ),
                pk=pk
            )
        else:
            # Обычные пользователи видят только опубликованные или свои продукты
            product = get_object_or_404(
                Product.objects.filter(
                    Q(is_published=True) | Q(owner=user)
                ),
                pk=pk
            )
    else:
        # Неавторизованные пользователи видят только опубликованные
        product = get_object_or_404(Product.objects.filter(is_published=True), pk=pk)

    context = {
        'product': product,
        'title': f'{product.name} - Детали'
    }
    return render(request, 'catalog/product_detail.html', context)


class ProductListView(ListView):
    """Список всех продуктов"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Модератор продуктов').exists():
                # Админы и модераторы видят все
                queryset = Product.objects.all().order_by('-created_at')
            elif user.groups.filter(name='Контент-менеджер').exists():
                # Контент-менеджеры видят все, кроме черновиков других пользователей
                queryset = Product.objects.exclude(
                    status='draft', owner__isnull=False
                ).exclude(
                    status='draft', owner=user
                ).order_by('-created_at')
            else:
                # Обычные пользователи видят опубликованные + свои продукты
                queryset = Product.objects.filter(
                    Q(is_published=True) | Q(owner=user)
                ).order_by('-created_at')
        else:
            # Неавторизованные - только опубликованные
            queryset = Product.objects.filter(is_published=True).order_by('-created_at')

        # ВАЖНО: всегда возвращаем QuerySet, даже если пустой
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем queryset для статистики
        queryset = self.get_queryset()

        # Статистика
        context['total_products'] = queryset.count()
        context['published_count'] = queryset.filter(is_published=True).count()
        context['draft_count'] = queryset.filter(status='draft').count()
        context['moderation_count'] = queryset.filter(status='moderation').count()
        context['rejected_count'] = queryset.filter(status='rejected').count()

        return context


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно создан!"

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Автоматически устанавливаем владельца
        form.instance.owner = self.request.user

        # По умолчанию ставим статус "черновик" для обычных пользователей
        # и "на модерации" для тех, кто может публиковать
        if self.request.user.has_perm('catalog.can_moderate_product'):
            form.instance.status = 'published'
        else:
            form.instance.status = 'draft'

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Редактирование продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно обновлен!"

    def get_form_kwargs(self):
        """Передаем пользователя в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        """Проверка прав доступа"""
        product = self.get_object()
        user = self.request.user

        # 1. Суперпользователь всегда может редактировать
        if user.is_superuser:
            return True

        # 2. Владелец может редактировать
        if product.owner == user:
            return True

        # 3. Модератор может редактировать
        if user.groups.filter(name='Модератор продуктов').exists():
            return True

        # 4. Контент-менеджер может редактировать
        if user.groups.filter(name='Контент-менеджер').exists():
            return True

        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Удаление продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт успешно удален!"

    def test_func(self):
        """Проверка прав доступа"""
        product = self.get_object()
        user = self.request.user

        # 1. Суперпользователь всегда может удалять
        if user.is_superuser:
            return True

        # 2. Владелец может удалять
        if product.owner == user:
            return True

        # 3. Модератор может удалять
        if user.groups.filter(name='Модератор продуктов').exists():
            return True

        return False


def unpublish_product(request, pk):
    """Отмена публикации продукта"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    product = get_object_or_404(Product, pk=pk)

    # Проверяем право can_unpublish_product
    if not request.user.has_perm('catalog.can_unpublish_product'):
        raise PermissionDenied("У вас нет прав для отмены публикации")

    if request.method == 'POST':
        # Получаем причину из формы
        reason = request.POST.get('reason', '')

        # Меняем статус
        product.status = 'draft'
        product.moderator_comment = f"Снято с публикации. Причина: {reason}"
        product.moderated_at = timezone.now()
        product.save()

        messages.success(request, f'Публикация продукта "{product.name}" отменена')
        return redirect('catalog:product_list')

    # GET запрос - показываем форму подтверждения
    return render(request, 'catalog/product_unpublish.html', {'product': product})


def moderate_product(request, pk, action):
    """Модерация продукта"""
    if not request.user.is_authenticated:
        return redirect('users:login')

    product = get_object_or_404(Product, pk=pk)

    # Проверяем право модерации
    if not request.user.has_perm('catalog.can_moderate_product'):
        raise PermissionDenied("У вас нет прав для модерации продуктов")

    if action == 'approve':
        product.status = 'published'
        message = f'Продукт "{product.name}" одобрен и опубликован'
    elif action == 'reject':
        product.status = 'rejected'
        message = f'Продукт "{product.name}" отклонен'
    else:
        messages.error(request, 'Неверное действие')
        return redirect('catalog:product_list')

    product.moderated_at = timezone.now()
    product.save()

    messages.success(request, message)
    return redirect('catalog:product_list')


from django.views.decorators.cache import cache_page
from django.conf import settings


@cache_page(60 * 15)  # Кешируем на 15 минут
def test_cache_view(request):
    """
    Тестовая страница для проверки кеширования.
    """
    import time

    current_time = time.time()

    context = {
        'current_time': current_time,
        'cache_enabled': settings.CACHE_ENABLED,
        'cache_timeout': 15,
    }

    return render(request, 'catalog/test_cache.html', context)