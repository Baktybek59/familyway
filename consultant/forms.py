from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ConsultantProfile, Consultation, ConsultationMessage, ConsultationReview, ConsultationCategory
from healthcare.models import Doctor


class ConsultantProfileForm(forms.ModelForm):
    """Форма для редактирования профиля консультанта"""
    class Meta:
        model = ConsultantProfile
        fields = [
            'specialization', 'license_number', 'experience_years', 
            'education', 'bio', 'consultation_fee', 'is_available'
        ]
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConsultationForm(forms.ModelForm):
    """Форма для создания консультации"""
    class Meta:
        model = Consultation
        fields = [
            'doctor', 'title', 'description', 'urgency', 
            'child_age_months', 'child_symptoms', 'medical_history', 'attachments'
        ]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'child_age_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'child_symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Фильтруем только активных врачей
        self.fields['doctor'].queryset = Doctor.objects.filter(
            is_active=True
        ).select_related('facility')
        
        # Добавляем пустое значение
        self.fields['doctor'].empty_label = _("Выберите врача")
        
        # Делаем поля необязательными
        self.fields['child_age_months'].required = False
        self.fields['child_symptoms'].required = False
        self.fields['medical_history'].required = False
        self.fields['attachments'].required = False
    
    def clean_attachments(self):
        """Валидация загружаемых файлов"""
        file = self.cleaned_data.get('attachments')
        if file:
            # Проверяем размер файла (максимум 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('Размер файла не должен превышать 10MB'))
            
            # Проверяем расширение файла
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(_('Разрешены только файлы: JPG, PNG, GIF, PDF, DOC, DOCX'))
        
        return file


class ConsultationMessageForm(forms.ModelForm):
    """Форма для отправки сообщения в консультации"""
    class Meta:
        model = ConsultationMessage
        fields = ['content', 'attachments']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': _('Введите ваше сообщение...')
            }),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].required = False


class ConsultationReviewForm(forms.ModelForm):
    """Форма для отзыва о консультации"""
    class Meta:
        model = ConsultationReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': _('Оставьте отзыв о консультации...')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].required = False


class ConsultationSearchForm(forms.Form):
    """Форма поиска консультантов"""
    specialization = forms.ChoiceField(
        choices=[('', _('Все специализации'))] + ConsultantProfile.SPECIALIZATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_experience = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Минимальный опыт (лет)')
        })
    )
    max_fee = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Максимальная стоимость'),
            'step': '0.01'
        })
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Поиск по имени или специализации...')
        })
    )
