from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import AutoType, Service, SparePart
from .models import Review
from django.core.validators import RegexValidator
import datetime
from .models import CustomUser, AutoType, Service, SparePart, Review

class CustomUserCreationForm(UserCreationForm):
    birth_day = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Дата рождения"
    )
    
    phone = forms.CharField(
        required=True,
        max_length=20,
        label="Номер телефона",
        validators=[RegexValidator(
            regex=r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$",
            message="Номер телефона должен быть в формате +375 (XX) XXX-XX-XX."
        )]
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'birth_day', 'phone', 'password1', 'password2')
    
    def clean_birth_day(self):
        birth_day = self.cleaned_data.get('birth_day')
        if birth_day:
            today = datetime.date.today()
            age = today.year - birth_day.year - ((today.month, today.day) < (birth_day.month, birth_day.day))
            if age < 18:
                raise forms.ValidationError("Вы должны быть не моложе 18 лет.")
        return birth_day
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.date_of_birth = self.cleaned_data['birth_day']
        # Если в вашей модели CustomUser отсутствует поле phone,
        # его следует добавить или сохранить номер телефона в связанную модель (например, Client).
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Выводим только те поля, которые клиент сам заполняет – оценка и текст отзыва.
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'placeholder': 'Оценка от 1 до 5'}),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв'}),
        }


class AutoTypeForm(forms.ModelForm):
    class Meta:
        model = AutoType
        fields = ['name']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']


class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['name', 'price', 'description', 'image']

