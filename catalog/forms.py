from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category
from django.utils.translation import gettext_lazy as _


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продукта"""

    # Список запрещенных слов
    FORBIDDEN_WORDS = [
        'казино',
        'криптовалюта',
        'крипта',
        'биржа',
        'дешево',
        'бесплатно',
        'обман',
        'полиция',
        'радар'
    ]

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание продукта',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите цену',
                'step': '0.01',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

        help_texts = {
            'status': _('Выберите статус продукта. Только модераторы могут публиковать продукты.'),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с учетом прав пользователя"""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Настраиваем доступные статусы в зависимости от прав пользователя
        if self.user:
            if self.user.has_perm('catalog.can_moderate_product'):
                # Модераторы могут выбирать любой статус
                self.fields['status'].choices = Product.STATUS_CHOICES
                self.fields['status'].help_text = _('Вы можете изменить статус продукта')
            else:
                # Обычные пользователи могут выбирать только черновик или отправить на модерацию
                self.fields['status'].choices = [
                    ('draft', 'Черновик'),
                    ('moderation', 'На модерацию'),
                ]
                self.fields['status'].help_text = _(
                    'Выберите "Черновик" чтобы сохранить как черновик или '
                    '"На модерацию" чтобы отправить на проверку модератору'
                )
        else:
            # Для неавторизованных пользователей скрываем поле статуса
            self.fields['status'].widget = forms.HiddenInput()

        # Добавляем дополнительные классы и атрибуты для каждого поля
        for field_name, field in self.fields.items():
            # Пропускаем скрытые поля
            if isinstance(field.widget, forms.HiddenInput):
                continue

            # Добавляем общие классы если их нет
            if 'class' not in field.widget.attrs:
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'

            # Добавляем дополнительные стили в зависимости от типа поля
            if field_name == 'name':
                field.widget.attrs.update({
                    'class': field.widget.attrs['class'] + ' form-control-lg',
                    'autofocus': 'autofocus'
                })
            elif field_name == 'price':
                field.widget.attrs.update({
                    'class': field.widget.attrs['class'] + ' text-success fw-bold'
                })
            elif field_name == 'description':
                field.widget.attrs.update({
                    'class': field.widget.attrs['class'] + ' resize-vertical',
                    'style': 'resize: vertical; min-height: 100px;'
                })
            elif field_name == 'image':
                field.widget.attrs.update({
                    'class': field.widget.attrs['class'] + ' file-input-custom',
                    'accept': 'image/*'
                })
            elif field_name == 'status':
                # Добавляем классы в зависимости от статуса для визуального отличия
                status_class = 'form-select'
                if self.instance and self.instance.pk:
                    if self.instance.status == 'published':
                        status_class += ' border-success'
                    elif self.instance.status == 'rejected':
                        status_class += ' border-danger'
                    elif self.instance.status == 'moderation':
                        status_class += ' border-warning'
                    elif self.instance.status == 'draft':
                        status_class += ' border-secondary'
                field.widget.attrs['class'] = status_class

    def clean_name(self):
        """Валидация названия продукта"""
        name = self.cleaned_data['name']

        # Проверка на запрещенные слова
        for word in self.FORBIDDEN_WORDS:
            if word.lower() in name.lower():
                raise forms.ValidationError(
                    f'Название продукта содержит запрещенное слово: "{word}"'
                )

        return name

    def clean_description(self):
        """Валидация описания продукта"""
        description = self.cleaned_data['description']

        if description:  # Проверяем только если описание не пустое
            # Проверка на запрещенные слова
            for word in self.FORBIDDEN_WORDS:
                if word.lower() in description.lower():
                    raise forms.ValidationError(
                        f'Описание продукта содержит запрещенное слово: "{word}"'
                    )

        return description

    def clean_price(self):
        """Кастомная валидация для поля цены"""
        price = self.cleaned_data['price']

        # Проверяем что цена не отрицательная
        if price is not None and price < 0:
            raise ValidationError(
                'Цена продукта не может быть отрицательной. Пожалуйста, введите корректное значение.'
            )

        # Проверяем что цена не равна нулю (опционально)
        if price == 0:
            raise ValidationError(
                'Цена продукта не может быть равна нулю. Пожалуйста, введите корректное значение.'
            )

        return price

    def clean(self):
        """Дополнительная валидация формы"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')

        # Проверяем, что обычные пользователи не могут публиковать продукты
        if self.user and not self.user.has_perm('catalog.can_moderate_product'):
            if status == 'published':
                raise ValidationError({
                    'status': 'Вы не можете опубликовать продукт. Только модераторы имеют это право.'
                })

        return cleaned_data


class ProductModerationForm(forms.ModelForm):
    """Форма для модерации продукта (только для модераторов)"""

    moderator_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите комментарий модератора (необязательно)',
            'rows': 3
        }),
        label='Комментарий модератора'
    )

    class Meta:
        model = Product
        fields = ['status', 'moderator_comment']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор статусов для модерации
        self.fields['status'].choices = [
            ('published', 'Опубликовать'),
            ('rejected', 'Отклонить'),
            ('draft', 'Вернуть в черновик'),
        ]


class ProductUnpublishForm(forms.Form):
    """Форма для отмены публикации продукта"""

    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите причину снятия с публикации',
            'rows': 3
        }),
        label='Причина снятия с публикации'
    )

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)