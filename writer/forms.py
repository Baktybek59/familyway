from django import forms
from django.utils.translation import gettext_lazy as _
from .models import WriterProfile
from blog.models import BlogPost


class WriterProfileForm(forms.ModelForm):
    """Форма для редактирования профиля писателя"""
    class Meta:
        model = WriterProfile
        fields = ['bio', 'specialization', 'experience_years', 'website', 'social_media']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'social_media': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BlogPostForm(forms.ModelForm):
    """Форма для создания/редактирования блог-поста"""
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'language', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        post = super().save(commit=False)
        if self.user:
            post.author = self.user
        if commit:
            post.save()
        return post
