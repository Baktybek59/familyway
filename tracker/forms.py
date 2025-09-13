from django import forms
from django.utils.translation import gettext_lazy as _
from .models import BabyGrowth, BabySleep, BabyCry, BabyFeeding, BabyVaccination
from accounts.models import Child


class BabyGrowthForm(forms.ModelForm):
    class Meta:
        model = BabyGrowth
        fields = ['child', 'height', 'weight', 'date', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'child': _('Ребёнок'),
            'height': _('Рост (см)'),
            'weight': _('Вес (кг)'),
            'date': _('Дата'),
            'notes': _('Заметки'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profile = user.parent_profile
                family = profile.family if profile else None
                if family:
                    self.fields['child'].queryset = Child.objects.filter(family=family)
                else:
                    self.fields['child'].queryset = Child.objects.none()
            except:
                self.fields['child'].queryset = Child.objects.none()
        else:
            self.fields['child'].queryset = Child.objects.none()


class BabySleepForm(forms.ModelForm):
    class Meta:
        model = BabySleep
        fields = ['child', 'date', 'hours_slept', 'sleep_quality', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hours_slept': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'sleep_quality': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'child': _('Ребёнок'),
            'date': _('Дата'),
            'hours_slept': _('Часы сна'),
            'sleep_quality': _('Качество сна'),
            'notes': _('Заметки'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profile = user.parent_profile
                family = profile.family if profile else None
                if family:
                    self.fields['child'].queryset = Child.objects.filter(family=family)
                else:
                    self.fields['child'].queryset = Child.objects.none()
            except:
                self.fields['child'].queryset = Child.objects.none()
        else:
            self.fields['child'].queryset = Child.objects.none()


class BabyCryForm(forms.ModelForm):
    class Meta:
        model = BabyCry
        fields = ['child', 'date', 'minutes_cried', 'reason', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'minutes_cried': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'child': _('Ребёнок'),
            'date': _('Дата'),
            'minutes_cried': _('Минуты плача'),
            'reason': _('Причина плача'),
            'notes': _('Заметки'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profile = user.parent_profile
                family = profile.family if profile else None
                if family:
                    self.fields['child'].queryset = Child.objects.filter(family=family)
                else:
                    self.fields['child'].queryset = Child.objects.none()
            except:
                self.fields['child'].queryset = Child.objects.none()
        else:
            self.fields['child'].queryset = Child.objects.none()


class BabyFeedingForm(forms.ModelForm):
    class Meta:
        model = BabyFeeding
        fields = ['child', 'date', 'time', 'feeding_type', 'amount', 'duration', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'feeding_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'child': _('Ребёнок'),
            'date': _('Дата'),
            'time': _('Время'),
            'feeding_type': _('Тип питания'),
            'amount': _('Количество'),
            'duration': _('Длительность (мин)'),
            'notes': _('Заметки'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profile = user.parent_profile
                family = profile.family if profile else None
                if family:
                    self.fields['child'].queryset = Child.objects.filter(family=family)
                else:
                    self.fields['child'].queryset = Child.objects.none()
            except:
                self.fields['child'].queryset = Child.objects.none()
        else:
            self.fields['child'].queryset = Child.objects.none()
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import BabyVaccination
from accounts.models import Child


class BabyVaccinationForm(forms.ModelForm):
    class Meta:
        model = BabyVaccination
        fields = ['child', 'vaccine_name', 'date_given', 'next_due_date', 'doctor_name', 'clinic_name', 'batch_number', 'reaction', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': 'form-control'}),
            'vaccine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: БЦЖ, АКДС, Полиомиелит'}),
            'date_given': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'doctor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО врача'}),
            'clinic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название медицинского учреждения'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер партии вакцины'}),
            'reaction': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите реакцию ребенка на вакцину'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Дополнительные заметки'}),
        }
        labels = {
            'child': _('Ребёнок'),
            'vaccine_name': _('Название вакцины'),
            'date_given': _('Дата вакцинации'),
            'next_due_date': _('Следующая вакцинация'),
            'doctor_name': _('Имя врача'),
            'clinic_name': _('Название клиники'),
            'batch_number': _('Номер партии'),
            'reaction': _('Реакция на вакцину'),
            'notes': _('Заметки'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profile = user.parent_profile
                family = profile.family if profile else None
                if family:
                    self.fields['child'].queryset = Child.objects.filter(family=family)
                else:
                    self.fields['child'].queryset = Child.objects.none()
            except:
                self.fields['child'].queryset = Child.objects.none()
        else:
            self.fields['child'].queryset = Child.objects.none()
