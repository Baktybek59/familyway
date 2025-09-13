from django import forms
from django.utils.translation import gettext_lazy as _
from .models import BlogComment


class BlogCommentForm(forms.ModelForm):
    """Форма для добавления комментария к статье блога"""
    
    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Оставьте ваш комментарий...'
            })
        }
        labels = {
            'content': _('Комментарий')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True




