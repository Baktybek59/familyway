from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class NotificationType(models.TextChoices):
    """Типы уведомлений"""
    # Системные уведомления
    SYSTEM_ANNOUNCEMENT = 'system_announcement', _('Системное объявление')
    SYSTEM_UPDATE = 'system_update', _('Обновление системы')
    SYSTEM_MAINTENANCE = 'system_maintenance', _('Техническое обслуживание')
    
    # Уведомления о консультациях
    CONSULTATION_REQUEST = 'consultation_request', _('Запрос на консультацию')
    CONSULTATION_ACCEPTED = 'consultation_accepted', _('Консультация принята')
    CONSULTATION_REJECTED = 'consultation_rejected', _('Консультация отклонена')
    CONSULTATION_COMPLETED = 'consultation_completed', _('Консультация завершена')
    CONSULTATION_MESSAGE = 'consultation_message', _('Сообщение в консультации')
    
    # Уведомления форума
    FORUM_TOPIC_REPLY = 'forum_topic_reply', _('Ответ в теме форума')
    FORUM_TOPIC_CREATED = 'forum_topic_created', _('Создана новая тема')
    FORUM_TOPIC_SOLUTION = 'forum_topic_solution', _('Тема отмечена как решение')
    FORUM_TOPIC_DELETED = 'forum_topic_deleted', _('Тема удалена')
    FORUM_POST_QUOTED = 'forum_post_quoted', _('Вас процитировали в форуме')
    
    # Уведомления об отзывах
    REVIEW_LEFT = 'review_left', _('Оставлен отзыв')
    REVIEW_APPROVED = 'review_approved', _('Отзыв одобрен')
    REVIEW_DELETED = 'review_deleted', _('Отзыв удален')
    REVIEW_RESPONSE = 'review_response', _('Ответ на отзыв')
    
    # Уведомления блога
    BLOG_POST_PUBLISHED = 'blog_post_published', _('Опубликована статья блога')
    BLOG_POST_APPROVED = 'blog_post_approved', _('Статья блога одобрена')
    BLOG_POST_REJECTED = 'blog_post_rejected', _('Статья блога отклонена')
    BLOG_COMMENT = 'blog_comment', _('Комментарий к статье')
    
    # Уведомления о заявках писателей
    WRITER_APPLICATION_SUBMITTED = 'writer_application_submitted', _('Подана заявка писателя')
    WRITER_APPLICATION_APPROVED = 'writer_application_approved', _('Заявка писателя одобрена')
    WRITER_APPLICATION_REJECTED = 'writer_application_rejected', _('Заявка писателя отклонена')
    
    # Уведомления медицинских учреждений
    FACILITY_NEW_REVIEW = 'facility_new_review', _('Новый отзыв об учреждении')
    FACILITY_NEW_DOCTOR_REVIEW = 'facility_new_doctor_review', _('Новый отзыв о враче')
    FACILITY_NEW_APPOINTMENT = 'facility_new_appointment', _('Новая запись к врачу')
    FACILITY_REQUEST_APPROVED = 'facility_request_approved', _('Заявка учреждения одобрена')
    FACILITY_REQUEST_REJECTED = 'facility_request_rejected', _('Заявка учреждения отклонена')
    
    # Уведомления трекера
    TRACKER_MILESTONE = 'tracker_milestone', _('Достигнута веха развития')
    TRACKER_VACCINATION_DUE = 'tracker_vaccination_due', _('Подошло время прививки')
    TRACKER_APPOINTMENT_REMINDER = 'tracker_appointment_reminder', _('Напоминание о приеме')
    
    # Уведомления техподдержки
    SUPPORT_TICKET_CREATED = 'support_ticket_created', _('Создан тикет техподдержки')
    SUPPORT_TICKET_UPDATED = 'support_ticket_updated', _('Тикет обновлен')
    SUPPORT_TICKET_RESOLVED = 'support_ticket_resolved', _('Тикет решен')


class NotificationPriority(models.TextChoices):
    """Приоритеты уведомлений"""
    LOW = 'low', _('Низкий')
    NORMAL = 'normal', _('Обычный')
    HIGH = 'high', _('Высокий')
    URGENT = 'urgent', _('Срочный')


class Notification(models.Model):
    """Основная модель уведомлений"""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('Получатель'))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications', verbose_name=_('Отправитель'))
    
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices, verbose_name=_('Тип уведомления'))
    priority = models.CharField(max_length=10, choices=NotificationPriority.choices, default=NotificationPriority.NORMAL, verbose_name=_('Приоритет'))
    
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    message = models.TextField(verbose_name=_('Сообщение'))
    
    # Связанные объекты (опционально)
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('ID связанного объекта'))
    related_object_type = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Тип связанного объекта'))
    
    # Статус
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    is_email_sent = models.BooleanField(default=False, verbose_name=_('Email отправлен'))
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Прочитано в'))
    
    # Дополнительные данные (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name=_('Дополнительные данные'))
    
    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Отметить как прочитанное"""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class NotificationSettings(models.Model):
    """Настройки уведомлений для пользователей"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings', verbose_name=_('Пользователь'))
    
    # Email уведомления
    email_enabled = models.BooleanField(default=True, verbose_name=_('Email уведомления включены'))
    email_consultations = models.BooleanField(default=True, verbose_name=_('Email о консультациях'))
    email_forum = models.BooleanField(default=True, verbose_name=_('Email о форуме'))
    email_reviews = models.BooleanField(default=True, verbose_name=_('Email об отзывах'))
    email_blog = models.BooleanField(default=True, verbose_name=_('Email о блоге'))
    email_system = models.BooleanField(default=True, verbose_name=_('Email системные'))
    email_tracker = models.BooleanField(default=True, verbose_name=_('Email о трекере'))
    
    # Push уведомления (для будущего развития)
    push_enabled = models.BooleanField(default=True, verbose_name=_('Push уведомления включены'))
    push_consultations = models.BooleanField(default=True, verbose_name=_('Push о консультациях'))
    push_forum = models.BooleanField(default=True, verbose_name=_('Push о форуме'))
    push_reviews = models.BooleanField(default=True, verbose_name=_('Push об отзывах'))
    push_blog = models.BooleanField(default=True, verbose_name=_('Push о блоге'))
    push_system = models.BooleanField(default=True, verbose_name=_('Push системные'))
    push_tracker = models.BooleanField(default=True, verbose_name=_('Push о трекере'))
    
    # Частота уведомлений
    digest_frequency = models.CharField(max_length=20, choices=[
        ('immediate', _('Немедленно')),
        ('hourly', _('Каждый час')),
        ('daily', _('Ежедневно')),
        ('weekly', _('Еженедельно')),
        ('never', _('Никогда')),
    ], default='immediate', verbose_name=_('Частота уведомлений'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    
    class Meta:
        verbose_name = _('Настройки уведомлений')
        verbose_name_plural = _('Настройки уведомлений')
    
    def __str__(self):
        return f"Настройки уведомлений {self.user.username}"


class NotificationTemplate(models.Model):
    """Шаблоны уведомлений"""
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices, unique=True, verbose_name=_('Тип уведомления'))
    title_template = models.CharField(max_length=200, verbose_name=_('Шаблон заголовка'))
    message_template = models.TextField(verbose_name=_('Шаблон сообщения'))
    
    # Настройки отправки
    send_email = models.BooleanField(default=True, verbose_name=_('Отправлять email'))
    send_push = models.BooleanField(default=True, verbose_name=_('Отправлять push'))
    
    # Приоритет по умолчанию
    default_priority = models.CharField(max_length=10, choices=NotificationPriority.choices, default=NotificationPriority.NORMAL, verbose_name=_('Приоритет по умолчанию'))
    
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    
    class Meta:
        verbose_name = _('Шаблон уведомления')
        verbose_name_plural = _('Шаблоны уведомлений')
    
    def __str__(self):
        return f"Шаблон {self.get_notification_type_display()}"