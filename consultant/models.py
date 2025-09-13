from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from accounts.models import Family


class ConsultantProfile(models.Model):
    """Профиль консультанта-врача"""
    SPECIALIZATION_CHOICES = [
        ('pediatrician', _('Педиатр')),
        ('neurologist', _('Невролог')),
        ('nutritionist', _('Диетолог')),
        ('psychologist', _('Детский психолог')),
        ('lactation', _('Консультант по грудному вскармливанию')),
        ('sleep', _('Консультант по сну')),
        ('development', _('Специалист по развитию')),
        ('other', _('Другое')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consultant_profile')
    specialization = models.CharField(
        max_length=20, 
        choices=SPECIALIZATION_CHOICES, 
        verbose_name=_('Специализация')
    )
    license_number = models.CharField(max_length=50, verbose_name=_('Номер лицензии'), blank=True)
    experience_years = models.PositiveIntegerField(verbose_name=_('Опыт работы (лет)'), default=0)
    education = models.TextField(verbose_name=_('Образование'), blank=True)
    bio = models.TextField(verbose_name=_('О себе'), blank=True)
    consultation_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name=_('Стоимость консультации')
    )
    is_available = models.BooleanField(default=True, verbose_name=_('Доступен для консультаций'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Верифицирован'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Рейтинг'))
    total_consultations = models.PositiveIntegerField(default=0, verbose_name=_('Всего консультаций'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль консультанта')
        verbose_name_plural = _('Профили консультантов')
    
    def __str__(self):
        return f"Доктор {self.user.get_full_name() or self.user.username} - {self.get_specialization_display()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Consultation(models.Model):
    """Модель консультации"""
    STATUS_CHOICES = [
        ('pending', _('Ожидает ответа')),
        ('in_progress', _('В процессе')),
        ('completed', _('Завершена')),
        ('cancelled', _('Отменена')),
    ]
    
    URGENCY_CHOICES = [
        ('low', _('Низкая')),
        ('medium', _('Средняя')),
        ('high', _('Высокая')),
        ('urgent', _('Срочно')),
    ]
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    consultant = models.ForeignKey(ConsultantProfile, on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    doctor = models.ForeignKey('healthcare.Doctor', on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name=_('Тема консультации'))
    description = models.TextField(verbose_name=_('Описание проблемы'))
    urgency = models.CharField(
        max_length=10, 
        choices=URGENCY_CHOICES, 
        default='medium',
        verbose_name=_('Срочность')
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Статус')
    )
    child_age_months = models.PositiveIntegerField(verbose_name=_('Возраст ребенка (месяцы)'), null=True, blank=True)
    child_symptoms = models.TextField(verbose_name=_('Симптомы'), blank=True)
    medical_history = models.TextField(verbose_name=_('Медицинская история'), blank=True)
    attachments = models.FileField(
        upload_to='consultation_attachments/', 
        blank=True, 
        null=True,
        verbose_name=_('Документы и анализы')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Консультация')
        verbose_name_plural = _('Консультации')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Консультация: {self.title} - {self.parent.username}"


class ConsultationMessage(models.Model):
    """Сообщения в консультации"""
    MESSAGE_TYPE_CHOICES = [
        ('question', _('Вопрос')),
        ('answer', _('Ответ')),
        ('follow_up', _('Уточнение')),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultation_messages')
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPE_CHOICES, 
        default='question',
        verbose_name=_('Тип сообщения')
    )
    content = models.TextField(verbose_name=_('Содержание'))
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    attachments = models.FileField(
        upload_to='consultation_attachments/', 
        blank=True, 
        null=True,
        verbose_name=_('Вложения')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Сообщение консультации')
        verbose_name_plural = _('Сообщения консультаций')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Сообщение от {self.sender.username} в консультации {self.consultation.id}"


class ConsultationReview(models.Model):
    """Отзывы о консультациях"""
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='review')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultation_reviews')
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Оценка')
    )
    comment = models.TextField(verbose_name=_('Комментарий'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Отзыв о консультации')
        verbose_name_plural = _('Отзывы о консультациях')
    
    def __str__(self):
        return f"Отзыв {self.rating}/5 от {self.parent.username}"


class ConsultationCategory(models.Model):
    """Категории консультаций"""
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), blank=True)
    icon = models.CharField(max_length=50, verbose_name=_('Иконка'), blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Категория консультаций')
        verbose_name_plural = _('Категории консультаций')
        ordering = ['name']
    
    def __str__(self):
        return self.name