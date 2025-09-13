from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class WriterProfile(models.Model):
    """Профиль писателя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='writer_profile')
    bio = models.TextField(verbose_name=_('Биография'), blank=True)
    specialization = models.CharField(max_length=200, verbose_name=_('Специализация'), blank=True)
    experience_years = models.PositiveIntegerField(verbose_name=_('Опыт работы (лет)'), default=0)
    website = models.URLField(verbose_name=_('Веб-сайт'), blank=True)
    social_media = models.CharField(max_length=200, verbose_name=_('Социальные сети'), blank=True)
    is_verified = models.BooleanField(default=False, verbose_name=_('Верифицирован'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль писателя')
        verbose_name_plural = _('Профили писателей')
    
    def __str__(self):
        return f"Писатель: {self.user.username}"
    
    @property
    def total_posts(self):
        """Общее количество опубликованных постов"""
        return self.user.blog_posts.filter(is_published=True).count()
    
    @property
    def total_views(self):
        """Общее количество просмотров постов"""
        return sum(post.views for post in self.user.blog_posts.filter(is_published=True))


class WriterDashboard(models.Model):
    """Дашборд писателя"""
    writer = models.OneToOneField(WriterProfile, on_delete=models.CASCADE, related_name='dashboard')
    last_login = models.DateTimeField(auto_now=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Общий заработок'))
    
    class Meta:
        verbose_name = _('Дашборд писателя')
        verbose_name_plural = _('Дашборды писателей')
    
    def __str__(self):
        return f"Дашборд {self.writer.user.username}"
