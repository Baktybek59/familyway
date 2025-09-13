from django.contrib import admin
from .models import BabyGrowth, BabySleep, BabyCry, BabyFeeding, BabyVaccination


@admin.register(BabyGrowth)
class BabyGrowthAdmin(admin.ModelAdmin):
    list_display = ['user', 'child', 'height', 'weight', 'date', 'created_at']
    list_filter = ['child', 'date', 'created_at']
    search_fields = ['user__username', 'child__name', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'child', 'height', 'weight', 'date')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BabySleep)
class BabySleepAdmin(admin.ModelAdmin):
    list_display = ['user', 'child', 'date', 'hours_slept', 'sleep_quality', 'created_at']
    list_filter = ['child', 'sleep_quality', 'date', 'created_at']
    search_fields = ['user__username', 'child__name', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'child', 'date', 'hours_slept', 'sleep_quality')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BabyCry)
class BabyCryAdmin(admin.ModelAdmin):
    list_display = ['user', 'child', 'date', 'minutes_cried', 'reason', 'created_at']
    list_filter = ['child', 'reason', 'date', 'created_at']
    search_fields = ['user__username', 'child__name', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'child', 'date', 'minutes_cried', 'reason')
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BabyFeeding)
class BabyFeedingAdmin(admin.ModelAdmin):
    list_display = ['user', 'child', 'date', 'time', 'feeding_type', 'amount', 'created_at']
    list_filter = ['child', 'feeding_type', 'date', 'created_at']
    search_fields = ['user__username', 'child__name', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'child', 'date', 'time', 'feeding_type')
        }),
        ('Дополнительно', {
            'fields': ('amount', 'duration', 'notes')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BabyVaccination)
class BabyVaccinationAdmin(admin.ModelAdmin):
    list_display = ['user', 'child', 'vaccine_name', 'date_given', 'next_due_date', 'doctor_name', 'created_at']
    list_filter = ['child', 'date_given', 'created_at']
    search_fields = ['user__username', 'child__name', 'vaccine_name', 'doctor_name', 'clinic_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'child', 'vaccine_name', 'date_given', 'next_due_date')
        }),
        ('Медицинская информация', {
            'fields': ('doctor_name', 'clinic_name', 'batch_number')
        }),
        ('Дополнительно', {
            'fields': ('reaction', 'notes')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
