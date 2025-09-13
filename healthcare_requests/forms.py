from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import HealthcareFacilityRequest
from healthcare.models import HealthcareCategory


class HealthcareFacilityRequestForm(forms.ModelForm):
    """Форма подачи заявки медицинского учреждения"""
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label=_('Подтвердите пароль')
    )
    
    class Meta:
        model = HealthcareFacilityRequest
        fields = [
            'facility_name', 'facility_type', 'description',
            'contact_person', 'email', 'phone', 'address', 'city',
            'username', 'password', 'license_document', 'additional_documents'
        ]
        widgets = {
            'facility_name': forms.TextInput(attrs={'class': 'form-control'}),
            'facility_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'license_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'additional_documents': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['facility_type'].queryset = HealthcareCategory.objects.all()
        self.fields['additional_documents'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(_('Пароли не совпадают'))
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(_('Пользователь с таким логином уже существует'))
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(_('Пользователь с таким email уже существует'))
        return email
    
    def clean_license_document(self):
        file = self.cleaned_data.get('license_document')
        if file:
            # Проверяем размер файла (максимум 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('Размер файла не должен превышать 5MB'))
            
            # Проверяем расширение файла
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(_('Разрешены только файлы: PDF, JPG, PNG'))
        
        return file


class FacilityRequestReviewForm(forms.ModelForm):
    """Форма рассмотрения заявки администратором"""
    
    class Meta:
        model = HealthcareFacilityRequest
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Введите заметки по заявке...')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin_notes'].required = False


class FacilityLoginForm(forms.Form):
    """Форма входа для медицинского учреждения"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Логин учреждения')
        }),
        label=_('Логин')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Пароль')
        }),
        label=_('Пароль')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True})
