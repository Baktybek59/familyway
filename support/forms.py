from django import forms
from django.contrib.auth.models import User
from .models import SupportTicket, TicketComment, SupportProfile, SupportDashboard
from django.utils.translation import gettext_lazy as _


class SupportProfileForm(forms.ModelForm):
    """Форма профиля техподдержки"""
    class Meta:
        model = SupportProfile
        fields = [
            'employee_id', 'department', 'phone', 'email', 'position', 
            'bio', 'avatar', 'birth_date', 'address', 'emergency_contact', 
            'emergency_phone', 'skills', 'languages', 'is_team_lead'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
            'is_team_lead': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].required = True
        self.fields['department'].required = True
        self.fields['phone'].required = True


class SupportProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля техподдержки (для самого сотрудника)"""
    class Meta:
        model = SupportProfile
        fields = [
            'phone', 'email', 'position', 'bio', 'avatar', 'birth_date', 
            'address', 'emergency_contact', 'emergency_phone', 'skills', 'languages'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ReviewDeletionForm(forms.Form):
    """Форма удаления отзыва с указанием причины"""
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Укажите причину удаления отзыва...'
        }),
        label='Причина удаления',
        help_text='Обязательно укажите причину удаления отзыва. Это сообщение будет отправлено пользователю.'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].required = True


class SupportTicketForm(forms.ModelForm):
    """Форма создания тикета"""
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['category'].required = True


class TicketCommentForm(forms.ModelForm):
    """Форма комментария к тикету"""
    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True


class TicketAssignmentForm(forms.ModelForm):
    """Форма назначения тикета"""
    class Meta:
        model = SupportTicket
        fields = ['assigned_to', 'status', 'priority']
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только активных сотрудников техподдержки
        self.fields['assigned_to'].queryset = SupportProfile.objects.filter(is_active=True)


class SupportDashboardForm(forms.ModelForm):
    """Форма настроек дашборда"""
    class Meta:
        model = SupportDashboard
        fields = [
            'show_open_tickets', 'show_high_priority', 'show_my_tickets',
            'show_facility_requests', 'show_forum_reports', 'show_blog_approvals'
        ]
        widgets = {
            'show_open_tickets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_high_priority': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_my_tickets': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_facility_requests': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_forum_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_blog_approvals': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DisputeTicketForm(forms.ModelForm):
    """Форма создания тикета для спора врач-родитель"""
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['description'].required = True
        # Устанавливаем категорию как спор
        self.initial['category'] = 'dispute'


class FacilityRequestReviewForm(forms.ModelForm):
    """Форма для рассмотрения заявки учреждения"""
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = SupportProfile.objects.filter(is_active=True)


class BlogApprovalForm(forms.ModelForm):
    """Форма для одобрения статей блога"""
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = SupportProfile.objects.filter(is_active=True)


class ForumModerationForm(forms.ModelForm):
    """Форма для модерации форума"""
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = SupportProfile.objects.filter(is_active=True)
