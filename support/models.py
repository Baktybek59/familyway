from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class SupportProfile(models.Model):
    """Профиль сотрудника техподдержки"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    employee_id = models.CharField(max_length=20, unique=True, verbose_name=_('ID сотрудника'))
    department = models.CharField(max_length=100, verbose_name=_('Отдел'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    position = models.CharField(max_length=100, blank=True, verbose_name=_('Должность'))
    bio = models.TextField(blank=True, verbose_name=_('О себе'))
    avatar = models.ImageField(upload_to='support/avatars/', blank=True, null=True, verbose_name=_('Аватар'))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_('Дата рождения'))
    address = models.TextField(blank=True, verbose_name=_('Адрес'))
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name=_('Контакт для экстренных случаев'))
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон экстренного контакта'))
    skills = models.TextField(blank=True, verbose_name=_('Навыки и компетенции'))
    languages = models.CharField(max_length=200, blank=True, verbose_name=_('Языки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    is_team_lead = models.BooleanField(default=False, verbose_name=_('Руководитель команды'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлен'))

    class Meta:
        verbose_name = _('Профиль техподдержки')
        verbose_name_plural = _('Профили техподдержки')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class SupportTicket(models.Model):
    """Тикеты техподдержки"""
    PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
        ('urgent', _('Срочный')),
    ]
    
    STATUS_CHOICES = [
        ('open', _('Открыт')),
        ('in_progress', _('В работе')),
        ('resolved', _('Решен')),
        ('closed', _('Закрыт')),
    ]
    
    CATEGORY_CHOICES = [
        ('dispute', _('Спорный вопрос врач-родитель')),
        ('facility_request', _('Заявка учреждения')),
        ('forum_moderation', _('Модерация форума')),
        ('blog_approval', _('Одобрение статей блога')),
        ('blog_creator', _('Добавление авторов блога')),
        ('review_moderation', _('Модерация отзывов')),
        ('other', _('Другое')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    description = models.TextField(verbose_name=_('Описание'))
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name=_('Категория'))
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('Приоритет'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name=_('Статус'))
    
    # Связанные объекты
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets', verbose_name=_('Создан пользователем'))
    assigned_to = models.ForeignKey(SupportProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name=_('Назначен'))
    
    # Связанные объекты для разных типов тикетов
    related_doctor = models.ForeignKey('healthcare.Doctor', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Связанный врач'))
    related_parent = models.ForeignKey('accounts.ParentProfile', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Связанный родитель'))
    related_facility_request = models.ForeignKey('healthcare_requests.HealthcareFacilityRequest', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Заявка учреждения'))
    related_forum_post = models.ForeignKey('forum.Post', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Пост форума'))
    related_blog_post = models.ForeignKey('blog.BlogPost', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Статья блога'))
    # related_review = models.ForeignKey('healthcare.Review', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Отзыв'))  # Временно отключено
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлен'))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Решен'))

    class Meta:
        verbose_name = _('Тикет техподдержки')
        verbose_name_plural = _('Тикеты техподдержки')
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"


class TicketComment(models.Model):
    """Комментарии к тикетам"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Тикет'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Автор'))
    content = models.TextField(verbose_name=_('Содержание'))
    is_internal = models.BooleanField(default=False, verbose_name=_('Внутренний комментарий'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))

    class Meta:
        verbose_name = _('Комментарий тикета')
        verbose_name_plural = _('Комментарии тикетов')
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий к #{self.ticket.id} от {self.author.username}"


class SupportNotification(models.Model):
    """Уведомления для техподдержки"""
    NOTIFICATION_TYPES = [
        ('new_ticket', _('Новый тикет')),
        ('ticket_assigned', _('Тикет назначен')),
        ('ticket_updated', _('Тикет обновлен')),
        ('ticket_resolved', _('Тикет решен')),
        ('facility_request', _('Новая заявка учреждения')),
        ('forum_report', _('Жалоба на форум')),
        ('blog_approval', _('Статья на одобрение')),
        ('review_report', _('Жалоба на отзыв')),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Получатель'))
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name=_('Тип уведомления'))
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    message = models.TextField(verbose_name=_('Сообщение'))
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    related_ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Связанный тикет'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))

    class Meta:
        verbose_name = _('Уведомление техподдержки')
        verbose_name_plural = _('Уведомления техподдержки')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class SupportDashboard(models.Model):
    """Дашборд техподдержки"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    
    # Настройки отображения
    show_open_tickets = models.BooleanField(default=True, verbose_name=_('Показывать открытые тикеты'))
    show_high_priority = models.BooleanField(default=True, verbose_name=_('Показывать высокий приоритет'))
    show_my_tickets = models.BooleanField(default=True, verbose_name=_('Показывать мои тикеты'))
    show_facility_requests = models.BooleanField(default=True, verbose_name=_('Показывать заявки учреждений'))
    show_forum_reports = models.BooleanField(default=True, verbose_name=_('Показывать жалобы форума'))
    show_blog_approvals = models.BooleanField(default=True, verbose_name=_('Показывать одобрения блога'))
    
    # Статистика
    tickets_resolved = models.PositiveIntegerField(default=0, verbose_name=_('Решенных тикетов'))
    average_resolution_time = models.DurationField(null=True, blank=True, verbose_name=_('Среднее время решения'))
    last_activity = models.DateTimeField(auto_now=True, verbose_name=_('Последняя активность'))

    class Meta:
        verbose_name = _('Дашборд техподдержки')
        verbose_name_plural = _('Дашборды техподдержки')

    def __str__(self):
        return f"Дашборд {self.user.username}"


# Удаляем старую модель ReviewDeletionNotification
# Теперь используем основную систему уведомлений