from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    UserChangeForm  # ← ДОБАВИТЬ AuthenticationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя в админке"""

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    """Форма для изменения пользователя в админке"""

    class Meta:
        model = User
        fields = ('email',)


# === ФОРМЫ ДЛЯ РЕГИСТРАЦИИ И АВТОРИЗАЦИИ ===

class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем подсказки
        self.fields['email'].widget.attrs.update({'placeholder': 'Введите email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Введите пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Подтвердите пароль'})


class UserLoginForm(AuthenticationForm):
    """Форма авторизации через email"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({'placeholder': 'Введите email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Введите пароль'})