from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ForumCategory, Topic, Post, ForumPoll, PollOption


class TopicForm(forms.ModelForm):
    """Форма создания/редактирования темы"""
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Теги через запятую (например: вопрос, помощь, ребенок)'),
            'data-role': 'tagsinput'
        }),
        help_text=_('Введите теги через запятую для лучшей категоризации')
    )
    
    class Meta:
        model = Topic
        fields = ['title', 'content', 'category', 'tags', 'is_announcement']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': _('Введите заголовок темы...'),
                'maxlength': 200
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Опишите вашу тему подробно...'),
                'style': 'resize: vertical;'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'is_announcement': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ForumCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = _('Выберите категорию...')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise forms.ValidationError(_('Заголовок должен содержать минимум 5 символов.'))
        return title.strip()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 10:
            raise forms.ValidationError(_('Содержание должно содержать минимум 10 символов.'))
        return content.strip()


class PostForm(forms.ModelForm):
    """Форма создания/редактирования сообщения"""
    
    class Meta:
        model = Post
        fields = ['content', 'parent_post']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': _('Напишите ваше сообщение...'),
                'style': 'resize: vertical;'
            }),
            'parent_post': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_post'].required = False

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 3:
            raise forms.ValidationError(_('Сообщение должно содержать минимум 3 символа.'))
        return content.strip()


class TopicSearchForm(forms.Form):
    """Форма поиска тем"""
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Поиск по темам...'),
            'aria-label': _('Поиск')
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=ForumCategory.objects.filter(is_active=True),
        required=False,
        empty_label=_('Все категории'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', _('Все статусы')),
            ('open', _('Открытые')),
            ('closed', _('Закрытые')),
            ('pinned', _('Закрепленные')),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class CategoryForm(forms.ModelForm):
    """Форма создания/редактирования категории (для админов)"""
    
    class Meta:
        model = ForumCategory
        fields = ['name', 'description', 'icon', 'color', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Название категории')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Описание категории')
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'bi-chat-dots',
                'help_text': _('Bootstrap Icons класс (например: bi-chat-dots)')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#007bff'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise forms.ValidationError(_('Название должно содержать минимум 2 символа.'))
        return name.strip()

    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        if icon and not icon.startswith('bi-'):
            raise forms.ValidationError(_('Иконка должна начинаться с "bi-" (Bootstrap Icons).'))
        return icon


class PollForm(forms.ModelForm):
    """Форма создания опроса"""
    
    class Meta:
        model = ForumPoll
        fields = ['question', 'is_multiple_choice', 'is_anonymous', 'expires_at']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите вопрос для опроса...'),
                'maxlength': 200
            }),
            'is_multiple_choice': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }


class PollOptionForm(forms.ModelForm):
    """Форма для вариантов ответов в опросе"""
    
    class Meta:
        model = PollOption
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Вариант ответа...'),
                'maxlength': 100
            })
        }


class PollVoteForm(forms.Form):
    """Форма голосования в опросе"""
    option = forms.ModelChoiceField(
        queryset=PollOption.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    
    def __init__(self, poll, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option'].queryset = poll.options.all()
        if poll.is_multiple_choice:
            self.fields['option'].widget = forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})


class ModerationForm(forms.Form):
    """Форма модерации"""
    ACTION_CHOICES = [
        ('topic_locked', _('Заблокировать тему')),
        ('topic_unlocked', _('Разблокировать тему')),
        ('topic_pinned', _('Закрепить тему')),
        ('topic_unpinned', _('Открепить тему')),
        ('topic_closed', _('Закрыть тему')),
        ('topic_opened', _('Открыть тему')),
        ('post_hidden', _('Скрыть сообщение')),
        ('post_shown', _('Показать сообщение')),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Причина модерации (необязательно)...')
        })
    )

