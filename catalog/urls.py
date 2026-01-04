# catalog/urls.py
from django.urls import path
from . import views
from .views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

app_name = 'catalog'

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('contacts/', views.contacts, name='contacts'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # CRUD операции с продуктами
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Действия модератора
    path('products/<int:pk>/unpublish/', views.unpublish_product, name='product_unpublish'),
    path('products/<int:pk>/moderate/<str:action>/', views.moderate_product, name='product_moderate'),

    # Тест кеширования (для задания 1)
    path('test-cache/', views.test_cache_view, name='test_cache'),

    # Продукты по категориям (для задания 3)
    path('category/<int:category_id>/', views.category_products, name='category_products'),
]