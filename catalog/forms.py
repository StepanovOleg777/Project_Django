from django import forms
from django.core.exceptions import ValidationError
from .models import Product


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
        fields = ['name', 'description', 'image', 'category', 'price']
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
                'class': 'form-select'  # Изменено на form-select для лучшего стиля
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите цену',
                'step': '0.01',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с дополнительной стилизацией"""
        super().__init__(*args, **kwargs)

        # Добавляем дополнительные классы и атрибуты для каждого поля
        for field_name, field in self.fields.items():
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