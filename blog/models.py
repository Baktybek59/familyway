from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('mom', _('Для мамы')),
        ('dad', _('Для папы')),
        ('general', _('Общие')),
    ]
    
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('ky', 'Кыргызча'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_('Автор'))
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество просмотров'))
    read_time = models.PositiveIntegerField(default=0, verbose_name=_('Время чтения (мин)'))
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name=_('Категория'))
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_('Язык'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    is_published = models.BooleanField(default=True, verbose_name=_('Опубликовано'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Одобрено'))
    status = models.CharField(max_length=20, choices=[
        ('draft', _('Черновик')),
        ('pending', _('На одобрении')),
        ('approved', _('Одобрено')),
        ('published', _('Опубликовано')),
        ('rejected', _('Отклонено')),
    ], default='draft', verbose_name=_('Статус'))
    
    class Meta:
        verbose_name = _('Статья блога')
        verbose_name_plural = _('Статьи блога')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post_detail', kwargs={'pk': self.pk})
    
    def get_likes_count(self):
        return self.likes.count()
    
    def get_dislikes_count(self):
        return self.dislikes.count()
    
    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def is_disliked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.dislikes.filter(user=user).exists()


class BlogComment(models.Model):
    """Комментарии к статьям блога"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Статья'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Автор'))
    content = models.TextField(verbose_name=_('Содержание'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    is_approved = models.BooleanField(default=True, verbose_name=_('Одобрено'))
    
    class Meta:
        verbose_name = _('Комментарий к статье')
        verbose_name_plural = _('Комментарии к статьям')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Комментарий к {self.post.title} от {self.author.username}"


class BlogLike(models.Model):
    """Лайки к статьям блога"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Статья'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Лайк статьи')
        verbose_name_plural = _('Лайки статей')
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"Лайк {self.user.username} к {self.post.title}"


class BlogDislike(models.Model):
    """Дизлайки к статьям блога"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='dislikes', verbose_name=_('Статья'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Дизлайк статьи')
        verbose_name_plural = _('Дизлайки статей')
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f"Дизлайк {self.user.username} к {self.post.title}"


class BlogAnalytics(models.Model):
    """Аналитика статей блога"""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='analytics', verbose_name=_('Статья'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_analytics', verbose_name=_('Пользователь'))
    view_duration = models.PositiveIntegerField(default=0, verbose_name=_('Время просмотра (сек)'))
    read_progress = models.PositiveIntegerField(default=0, verbose_name=_('Прогресс чтения (%)'))
    user_age = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Возраст пользователя'))
    user_gender = models.CharField(max_length=10, choices=[
        ('male', _('Мужской')),
        ('female', _('Женский')),
        ('other', _('Другой')),
    ], blank=True, verbose_name=_('Пол пользователя'))
    user_city = models.CharField(max_length=100, blank=True, verbose_name=_('Город пользователя'))
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', _('Десктоп')),
        ('mobile', _('Мобильный')),
        ('tablet', _('Планшет')),
    ], default='desktop', verbose_name=_('Тип устройства'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Аналитика статьи')
        verbose_name_plural = _('Аналитика статей')
        unique_together = ['blog_post', 'user']
    
    def __str__(self):
        return f"{self.blog_post.title} - {self.user.username}"