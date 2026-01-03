from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, Category
from .forms import ProductForm


# Существующие функции остаются
def home(request):
    """Контроллер главной страницы - ОСТАЕТСЯ ОБЩЕДОСТУПНЫМ"""
    products = Product.objects.all()
    context = {
        'products': products,
        'title': 'Главная - Магазин'
    }
    return render(request, "catalog/home.html", context)


def contacts(request):
    """Контакты - ОСТАЕТСЯ ОБЩЕДОСТУПНЫМ"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        return render(request, "catalog/contacts.html", {"success": True})
    return render(request, "catalog/contacts.html")


def product_detail(request, pk):
    """Страница товара - ОСТАЕТСЯ ОБЩЕДОСТУПНОЙ"""
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
        'title': f'{product.name} - Детали'
    }
    return render(request, 'catalog/product_detail.html', context)


# Новые классы для CRUD операций

class ProductListView(ListView):
    """Список всех продуктов - ОСТАЕТСЯ ОБЩЕДОСТУПНЫМ"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'


# === ДОБАВИТЬ LoginRequiredMixin к защищенным контроллерам ===

class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового продукта - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно создан!"


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование продукта - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно обновлен!"


class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление продукта - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт успешно удален!"