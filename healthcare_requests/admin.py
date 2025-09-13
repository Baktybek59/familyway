from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import HealthcareFacilityRequest, FacilityDashboard, FacilityNotification


@admin.register(HealthcareFacilityRequest)
class HealthcareFacilityRequestAdmin(admin.ModelAdmin):
    list_display = [
        'facility_name', 'facility_type', 'contact_person', 
        'email', 'status', 'created_at', 'processed_at'
    ]
    list_filter = [
        'status', 'facility_type', 'created_at', 'processed_at'
    ]
    search_fields = [
        'facility_name', 'contact_person', 'email', 'username'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'processed_at'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'facility_name', 'facility_type', 'description',
                'contact_person', 'email', 'phone'
            )
        }),
        ('Адрес', {
            'fields': ('address', 'city')
        }),
        ('Учетные данные', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('Документы', {
            'fields': ('license_document', 'additional_documents'),
            'classes': ('collapse',)
        }),
        ('Обработка', {
            'fields': ('status', 'admin_notes', 'processed_by', 'processed_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('facility_type', 'processed_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая заявка
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FacilityDashboard)
class FacilityDashboardAdmin(admin.ModelAdmin):
    list_display = [
        'facility_request', 'total_doctors', 'total_consultations',
        'total_reviews', 'average_rating', 'is_active', 'last_activity'
    ]
    list_filter = ['is_active', 'last_activity', 'created_at']
    search_fields = ['facility_request__facility_name']
    readonly_fields = [
        'total_doctors', 'total_consultations', 'total_reviews',
        'average_rating', 'created_at', 'updated_at', 'last_activity'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('facility_request', 'is_active')
        }),
        ('Статистика', {
            'fields': (
                'total_doctors', 'total_consultations', 'total_reviews', 'average_rating'
            )
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('facility_request')


@admin.register(FacilityNotification)
class FacilityNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'facility_request', 'notification_type', 'title', 
        'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = [
        'facility_request__facility_name', 'title', 'message'
    ]
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('facility_request', 'notification_type', 'title', 'message')
        }),
        ('Статус', {
            'fields': ('is_read',)
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('facility_request')