from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from healthcare.models import HealthcareCategory


class HealthcareFacilityRequest(models.Model):
    """Заявка медицинского учреждения на добавление в каталог"""
    
    STATUS_CHOICES = [
        ('pending', _('Ожидает рассмотрения')),
        ('approved', _('Одобрена')),
        ('rejected', _('Отклонена')),
        ('needs_revision', _('Требует доработки')),
    ]
    
    # Основная информация
    facility_name = models.CharField(max_length=200, verbose_name=_('Название учреждения'))
    facility_type = models.ForeignKey(
        HealthcareCategory, 
        on_delete=models.CASCADE, 
        verbose_name=_('Тип учреждения')
    )
    description = models.TextField(verbose_name=_('Описание учреждения'))
    
    # Контактная информация
    contact_person = models.CharField(max_length=100, verbose_name=_('Контактное лицо'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    
    # Адрес
    address = models.TextField(verbose_name=_('Адрес'))
    city = models.CharField(max_length=100, verbose_name=_('Город'))
    
    # Учетные данные для входа
    username = models.CharField(max_length=150, verbose_name=_('Логин'))
    password = models.CharField(max_length=128, verbose_name=_('Пароль'))
    
    # Документы
    license_document = models.FileField(
        upload_to='facility_requests/licenses/',
        verbose_name=_('Лицензия'),
        help_text=_('Загрузите копию лицензии на медицинскую деятельность')
    )
    additional_documents = models.FileField(
        upload_to='facility_requests/documents/',
        blank=True,
        null=True,
        verbose_name=_('Дополнительные документы')
    )
    
    # Статус и обработка
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус заявки')
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name=_('Заметки администратора')
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_facility_requests',
        verbose_name=_('Обработано администратором')
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата обработки')
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Заявка медицинского учреждения')
        verbose_name_plural = _('Заявки медицинских учреждений')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.facility_name} - {self.get_status_display()}"
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        return self.status == 'rejected'


class FacilityDashboard(models.Model):
    """Дашборд медицинского учреждения"""
    
    facility_request = models.OneToOneField(
        HealthcareFacilityRequest,
        on_delete=models.CASCADE,
        related_name='dashboard',
        verbose_name=_('Заявка учреждения')
    )
    
    # Статистика
    total_doctors = models.PositiveIntegerField(default=0, verbose_name=_('Всего врачей'))
    total_consultations = models.PositiveIntegerField(default=0, verbose_name=_('Всего консультаций'))
    total_reviews = models.PositiveIntegerField(default=0, verbose_name=_('Всего отзывов'))
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name=_('Средний рейтинг')
    )
    
    # Настройки
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_('Последняя активность'))
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Дашборд учреждения')
        verbose_name_plural = _('Дашборды учреждений')
    
    def __str__(self):
        return f"Дашборд {self.facility_request.facility_name}"
    
    def update_statistics(self):
        """Обновляет статистику учреждения"""
        from healthcare.models import Doctor, DoctorReview
        
        # Подсчитываем врачей
        self.total_doctors = Doctor.objects.filter(
            facility__name=self.facility_request.facility_name
        ).count()
        
        # Подсчитываем консультации
        from consultant.models import Consultation
        self.total_consultations = Consultation.objects.filter(
            doctor__facility__name=self.facility_request.facility_name
        ).count()
        
        # Подсчитываем отзывы и рейтинг
        reviews = DoctorReview.objects.filter(
            doctor__facility__name=self.facility_request.facility_name
        )
        self.total_reviews = reviews.count()
        
        if reviews.exists():
            self.average_rating = reviews.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating'] or 0
        else:
            self.average_rating = 0
        
        self.save()


class FacilityNotification(models.Model):
    """Уведомления для медицинских учреждений"""
    
    NOTIFICATION_TYPES = [
        ('request_approved', _('Заявка одобрена')),
        ('request_rejected', _('Заявка отклонена')),
        ('new_consultation', _('Новая консультация')),
        ('new_review', _('Новый отзыв')),
        ('system_update', _('Обновление системы')),
    ]
    
    facility_request = models.ForeignKey(
        HealthcareFacilityRequest,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Заявка учреждения')
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name=_('Тип уведомления')
    )
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    message = models.TextField(verbose_name=_('Сообщение'))
    
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Уведомление учреждения')
        verbose_name_plural = _('Уведомления учреждений')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.facility_request.facility_name} - {self.title}"