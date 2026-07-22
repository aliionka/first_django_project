from django import forms
from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'description',
            'discount',
            'promotion_start_date',
            'promotion_end_date',
            'stock_availability',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'promotion_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'promotion_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'stock_availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше 0")
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть от 0 до 100")
        return discount


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'user',
            'products',
            'address',
            'comment',
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}), # Select для ForeignKey
            'products': forms.CheckboxSelectMultiple(attrs={
                'class': 'product-checkbox',
                'style': 'vertical-align: middle;'
            }), # или SelectMultiple для ManyToMany
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'user': '👤 Пользователь',
            'products': '📦 Товары',
            'address': '📍 Адрес доставки',
            'comment': '📝 Комментарий',
        }
        help_texts = {
            'products': 'Выберите один или несколько товаров',
            'address': 'Укажите точный адрес для доставки',
        }