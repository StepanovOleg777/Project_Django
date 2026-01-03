from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView

from .forms import UserRegisterForm, UserLoginForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        # Сначала сохраняем пользователя
        response = super().form_valid(form)

        # Отправляем приветственное письмо
        user_email = form.cleaned_data.get('email')
        send_mail(
            subject='Добро пожаловать в наш интернет-магазин!',
            message=f'Вы успешно зарегистрировались на сайте.\nВаш email: {user_email}\nПриятных покупок!',
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@myshop.com',
            recipient_list=[user_email],
            fail_silently=False,
        )
        return response


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        # После входа перенаправляем на главную страницу каталога
        return reverse_lazy('catalog:home')