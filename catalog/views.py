from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Product, Category
from .forms import ProductForm


# Существующие функции остаются
def home(request):
    """Контроллер главной страницы"""
    products = Product.objects.all()

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
    product = get_object_or_404(Product, pk=pk)

    context = {
        'product': product,
        'title': f'{product.name} - Детали'
    }
    return render(request, 'catalog/product_detail.html', context)


# Новые классы для CRUD операций с сообщениями
class ProductListView(ListView):
    """Список всех продуктов"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'


class ProductCreateView(SuccessMessageMixin, CreateView):
    """Создание нового продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно создан!"


class ProductUpdateView(SuccessMessageMixin, UpdateView):
    """Редактирование продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт '%(name)s' успешно обновлен!"


class ProductDeleteView(SuccessMessageMixin, DeleteView):
    """Удаление продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    success_message = "Продукт успешно удален!"