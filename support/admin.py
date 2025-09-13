from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SupportProfile, SupportTicket, TicketComment, SupportNotification, SupportDashboard


@admin.register(SupportProfile)
class SupportProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id', 'department']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'employee_id', 'department', 'phone', 'is_active')
        }),
        (_('Временные метки'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'priority', 'status', 'created_by', 'assigned_to', 'created_at']
    list_filter = ['category', 'priority', 'status', 'created_at', 'assigned_to']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'description', 'category', 'priority', 'status')
        }),
        (_('Назначение'), {
            'fields': ('created_by', 'assigned_to')
        }),
        (_('Связанные объекты'), {
            'fields': ('related_doctor', 'related_parent', 'related_facility_request', 
                      'related_forum_post', 'related_blog_post', 'related_review'),
            'classes': ('collapse',)
        }),
        (_('Временные метки'), {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['ticket__title', 'author__username', 'content']
    readonly_fields = ['created_at']


@admin.register(SupportNotification)
class SupportNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']


@admin.register(SupportDashboard)
class SupportDashboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'tickets_resolved', 'last_activity']
    search_fields = ['user__username']
    readonly_fields = ['last_activity']


# ReviewDeletionNotification теперь управляется через основную систему уведомлений