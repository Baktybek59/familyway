from django import forms
from django.utils.translation import gettext_lazy as _
from .models import HealthcareFacility, Doctor, DoctorReview, FacilityReview


class HealthcareFacilityForm(forms.ModelForm):
    class Meta:
        model = HealthcareFacility
        fields = ['category', 'name', 'description', 'address', 'phone', 'email', 'website', 'working_hours']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название медицинского учреждения'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание учреждения'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Полный адрес'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 XXX XXX XXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'working_hours': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Пн-Пт: 9:00-18:00, Сб: 9:00-14:00'}),
        }
        labels = {
            'category': _('Категория'),
            'name': _('Название'),
            'description': _('Описание'),
            'address': _('Адрес'),
            'phone': _('Телефон'),
            'email': _('Email'),
            'website': _('Веб-сайт'),
            'working_hours': _('Часы работы'),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['facility', 'first_name', 'last_name', 'middle_name', 'specialization', 'experience_years', 
                 'education', 'qualifications', 'phone', 'email', 'photo', 'bio']
        widgets = {
            'facility': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Специализация'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Образование'}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Квалификации'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+996 XXX XXX XXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Биография врача'}),
        }
        labels = {
            'facility': _('Медицинское учреждение'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'middle_name': _('Отчество'),
            'specialization': _('Специализация'),
            'experience_years': _('Опыт работы (лет)'),
            'education': _('Образование'),
            'qualifications': _('Квалификации'),
            'phone': _('Телефон'),
            'email': _('Email'),
            'photo': _('Фото'),
            'bio': _('Биография'),
        }


class DoctorReviewForm(forms.ModelForm):
    class Meta:
        model = DoctorReview
        fields = ['rating', 'title', 'comment', 'visit_date', 'is_anonymous']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок отзыва'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите ваш опыт посещения врача'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'rating': _('Оценка'),
            'title': _('Заголовок отзыва'),
            'comment': _('Комментарий'),
            'visit_date': _('Дата посещения'),
            'is_anonymous': _('Анонимный отзыв'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            (1, '1 - Очень плохо'),
            (2, '2 - Плохо'),
            (3, '3 - Удовлетворительно'),
            (4, '4 - Хорошо'),
            (5, '5 - Отлично'),
        ]


class FacilityReviewForm(forms.ModelForm):
    class Meta:
        model = FacilityReview
        fields = ['rating', 'title', 'comment', 'visit_date', 'is_anonymous']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок отзыва'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите ваш опыт посещения учреждения'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'rating': _('Оценка'),
            'title': _('Заголовок отзыва'),
            'comment': _('Комментарий'),
            'visit_date': _('Дата посещения'),
            'is_anonymous': _('Анонимный отзыв'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            (1, '1 - Очень плохо'),
            (2, '2 - Плохо'),
            (3, '3 - Удовлетворительно'),
            (4, '4 - Хорошо'),
            (5, '5 - Отлично'),
        ]


class DoctorLoginForm(forms.Form):
    """Форма входа для врачей"""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'doctor@example.com',
            'required': True
        })
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'required': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'autocomplete': 'email',
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'autocomplete': 'current-password'
        })


class DoctorProfileForm(forms.ModelForm):
    """Форма редактирования профиля врача"""
    class Meta:
        model = Doctor
        fields = [
            'first_name', 'last_name', 'middle_name', 'specialization', 
            'experience_years', 'education', 'qualifications', 'phone', 
            'email', 'photo', 'bio', 'working_hours', 'languages', 
            'awards', 'publications', 'consultation_price', 
            'consultation_duration', 'is_available_for_consultation'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'working_hours': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
            'awards': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'publications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'consultation_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'consultation_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 120}),
            'is_available_for_consultation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'middle_name': _('Отчество'),
            'specialization': _('Специализация'),
            'experience_years': _('Опыт работы (лет)'),
            'education': _('Образование'),
            'qualifications': _('Квалификации'),
            'phone': _('Телефон'),
            'email': _('Email'),
            'photo': _('Фото'),
            'bio': _('Биография'),
            'working_hours': _('Часы работы'),
            'languages': _('Языки'),
            'awards': _('Награды и достижения'),
            'publications': _('Публикации'),
            'consultation_price': _('Цена консультации (сом)'),
            'consultation_duration': _('Длительность консультации (мин)'),
            'is_available_for_consultation': _('Доступен для консультаций'),
        }


class DoctorPasswordForm(forms.Form):
    """Форма смены пароля врача"""
    current_password = forms.CharField(
        label=_('Текущий пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label=_('Подтвердите новый пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_('Пароли не совпадают'))
        
        return cleaned_data
