from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    """Форма для изменения пользователя"""

    class Meta:
        model = User
        fields = ('email',)