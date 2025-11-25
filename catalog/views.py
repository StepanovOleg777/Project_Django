from django.shortcuts import render, get_object_or_404
from .models import Product


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
        # Обработка формы (для дополнительного задания)
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        # Здесь можно добавить логику сохранения или отправки email
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