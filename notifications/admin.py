from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notification, NotificationSettings, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'recipient', 'notification_type', 'title', 'priority', 
        'is_read', 'is_email_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read', 'is_email_sent', 'created_at'
    ]
    search_fields = [
        'recipient__username', 'recipient__email', 'title', 'message'
    ]
    readonly_fields = ['created_at', 'read_at']
    list_editable = ['is_read', 'is_email_sent']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('recipient', 'sender', 'notification_type', 'priority')
        }),
        (_('Содержание'), {
            'fields': ('title', 'message')
        }),
        (_('Связанные объекты'), {
            'fields': ('related_object_id', 'related_object_type', 'extra_data'),
            'classes': ('collapse',)
        }),
        (_('Статус'), {
            'fields': ('is_read', 'is_email_sent', 'read_at')
        }),
        (_('Временные метки'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'push_enabled', 'digest_frequency', 'updated_at'
    ]
    list_filter = [
        'email_enabled', 'push_enabled', 'digest_frequency', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('user',)
        }),
        (_('Email уведомления'), {
            'fields': (
                'email_enabled', 'email_consultations', 'email_forum', 
                'email_reviews', 'email_blog', 'email_system', 'email_tracker'
            )
        }),
        (_('Push уведомления'), {
            'fields': (
                'push_enabled', 'push_consultations', 'push_forum', 
                'push_reviews', 'push_blog', 'push_system', 'push_tracker'
            )
        }),
        (_('Настройки'), {
            'fields': ('digest_frequency',)
        }),
        (_('Временные метки'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'notification_type', 'title_template', 'send_email', 'send_push', 
        'default_priority', 'is_active', 'updated_at'
    ]
    list_filter = [
        'send_email', 'send_push', 'default_priority', 'is_active', 'created_at'
    ]
    search_fields = ['notification_type', 'title_template']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'send_email', 'send_push']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('notification_type', 'is_active')
        }),
        (_('Шаблоны'), {
            'fields': ('title_template', 'message_template')
        }),
        (_('Настройки отправки'), {
            'fields': ('send_email', 'send_push', 'default_priority')
        }),
        (_('Временные метки'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )