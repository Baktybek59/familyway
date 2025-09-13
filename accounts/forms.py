from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import ParentProfile, WriterProfile, Child, WriterApplication


class ParentRegistrationForm(UserCreationForm):
    """Форма регистрации родителей"""
    ROLE_CHOICES = [
        ('mom', _('Я мама')),
        ('dad', _('Я папа')),
    ]
    
    first_name = forms.CharField(max_length=100, required=True, label=_('Имя'))
    last_name = forms.CharField(max_length=100, required=True, label=_('Фамилия'))
    email = forms.EmailField(required=True, label=_('Email'))
    phone = forms.CharField(max_length=20, required=False, label=_('Телефон'))
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=False, 
        label=_('Роль в семье'),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Создаем профиль родителя
            parent_profile = ParentProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone'],
                role=self.cleaned_data['role'],
                user_type='parent'
            )
            
        
        return user


class WriterLoginForm(forms.Form):
    """Форма входа для писателей"""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'writer@example.com',
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


class WriterProfileForm(forms.ModelForm):
    """Форма редактирования профиля писателя"""
    class Meta:
        model = WriterProfile
        fields = [
            'first_name', 'last_name', 'middle_name', 'email', 'phone', 
            'photo', 'bio', 'writing_motivation', 'journalism_experience', 
            'years_experience', 'specialization', 'languages'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'writing_motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'journalism_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'middle_name': _('Отчество'),
            'email': _('Email'),
            'phone': _('Телефон'),
            'photo': _('Фото'),
            'bio': _('Биография'),
            'writing_motivation': _('Почему хотите стать писателем?'),
            'journalism_experience': _('Опыт в журналистике'),
            'years_experience': _('Годы опыта'),
            'specialization': _('Специализация'),
            'languages': _('Языки'),
        }


class WriterPasswordForm(forms.Form):
    """Форма смены пароля писателя"""
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


class ParentProfileForm(forms.ModelForm):
    """Форма редактирования профиля родителя"""
    class Meta:
        model = ParentProfile
        fields = ['phone_number', 'city', 'workplace', 'birth_date', 'role', 'photo']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'phone_number': _('Телефон'),
            'city': _('Город'),
            'workplace': _('Место работы'),
            'birth_date': _('Дата рождения'),
            'role': _('Роль в семье'),
            'photo': _('Фотография профиля'),
        }
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Проверяем размер файла (максимум 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('Размер файла не должен превышать 5MB.'))
            
            # Проверяем тип файла
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if photo.content_type not in allowed_types:
                raise forms.ValidationError(_('Поддерживаются только файлы изображений (JPEG, PNG, GIF, WebP).'))
        
        return photo


class FamilyConnectForm(forms.Form):
    """Форма подключения к семье"""
    family_code = forms.CharField(
        max_length=8,
        label=_('Код семьи'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите код семьи',
            'maxlength': '8'
        })
    )


class ChildForm(forms.ModelForm):
    """Форма добавления/редактирования ребенка"""
    class Meta:
        model = Child
        fields = ['name', 'gender', 'birth_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': _('Имя ребенка'),
            'gender': _('Пол'),
            'birth_date': _('Дата рождения'),
        }


class WriterApplicationForm(forms.ModelForm):
    """Форма заявки на роль писателя"""
    password_confirm = forms.CharField(
        label=_('Подтвердите пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_('Введите пароль еще раз для подтверждения')
    )
    
    class Meta:
        model = WriterApplication
        fields = [
            'first_name', 'last_name', 'middle_name', 'email', 'phone',
            'username', 'password',
            'writing_motivation', 'journalism_experience', 'years_experience',
            'specialization', 'languages'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'writing_motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'journalism_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'middle_name': _('Отчество'),
            'email': _('Email'),
            'phone': _('Телефон'),
            'username': _('Логин'),
            'password': _('Пароль'),
            'writing_motivation': _('Почему хотите стать писателем?'),
            'journalism_experience': _('Опыт в журналистике'),
            'years_experience': _('Годы опыта'),
            'specialization': _('Специализация'),
            'languages': _('Языки'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем обязательными основные поля
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['username'].required = True
        self.fields['password'].required = True
        self.fields['password_confirm'].required = True
        self.fields['writing_motivation'].required = True
        self.fields['journalism_experience'].required = True
        self.fields['years_experience'].required = True
        
        # Добавляем help_text для логина
        self.fields['username'].help_text = _('Логин для входа в систему. Может содержать только буквы, цифры и символы @/./+/-/_')
        self.fields['password'].help_text = _('Пароль должен содержать минимум 8 символов')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Проверяем, что логин не занят в Django User
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError(_('Пользователь с таким логином уже существует'))
            
            # Проверяем, что логин не занят в заявках (исключая текущую заявку)
            existing_apps = WriterApplication.objects.filter(username=username)
            if self.instance and self.instance.pk:
                existing_apps = existing_apps.exclude(pk=self.instance.pk)
            
            if existing_apps.exists():
                raise forms.ValidationError(_('Заявка с таким логином уже подана'))
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(_('Пароли не совпадают'))
            
            if len(password) < 8:
                raise forms.ValidationError(_('Пароль должен содержать минимум 8 символов'))
        
        return cleaned_data
    
    def save(self, commit=True):
        application = super().save(commit=False)
        # Хешируем пароль перед сохранением
        from django.contrib.auth.hashers import make_password
        application.password = make_password(self.cleaned_data['password'])
        
        if commit:
            application.save()
        
        return application