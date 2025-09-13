from django.contrib import admin
from .models import WriterProfile, WriterDashboard


@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'experience_years', 'created_at']
    search_fields = ['user__username', 'user__email', 'specialization']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'bio', 'specialization', 'experience_years')
        }),
        ('Контакты', {
            'fields': ('website', 'social_media')
        }),
        ('Статус', {
            'fields': ('is_verified',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WriterDashboard)
class WriterDashboardAdmin(admin.ModelAdmin):
    list_display = ['writer', 'last_login', 'total_earnings']
    list_filter = ['last_login']
    readonly_fields = ['last_login']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('writer', 'total_earnings')
        }),
        ('Временные метки', {
            'fields': ('last_login',)
        }),
    )
