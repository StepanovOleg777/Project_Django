from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product


class HomeView(ListView):
    """CBV для главной страницы"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная - Магазин'
        return context


class ProductDetailView(DetailView):
    """CBV для страницы одного товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name} - Детали'
        return context


class ContactsView(TemplateView):
    """CBV для страницы контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса для формы контактов"""
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Здесь можно добавить логику сохранения или отправки email
        context = self.get_context_data()
        context['success'] = True
        return render(request, self.template_name, context)