from django.contrib import admin
from .models import HealthcareCategory, HealthcareFacility, Doctor, DoctorReview, FacilityReview


@admin.register(HealthcareCategory)
class HealthcareCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'order', 'facilities_count']
    list_filter = ['color']
    search_fields = ['name']
    ordering = ['order', 'name']
    
    def facilities_count(self, obj):
        return obj.facilities.count()
    facilities_count.short_description = 'Количество учреждений'


@admin.register(HealthcareFacility)
class HealthcareFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'address', 'phone', 'rating', 'reviews_count', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email']
    readonly_fields = ['rating', 'reviews_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'description', 'is_active')
        }),
        ('Контактная информация', {
            'fields': ('address', 'phone', 'email', 'website', 'working_hours')
        }),
        ('Статистика', {
            'fields': ('rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'facility', 'consultant', 'specialization', 'experience_years', 'rating', 'reviews_count', 'is_active', 'created_at']
    list_filter = ['facility', 'consultant', 'specialization', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'specialization', 'facility__name', 'consultant__user__username']
    readonly_fields = ['rating', 'reviews_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('facility', 'consultant', 'first_name', 'last_name', 'middle_name', 'specialization', 'is_active')
        }),
        ('Профессиональная информация', {
            'fields': ('experience_years', 'education', 'qualifications')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email', 'photo')
        }),
        ('Дополнительно', {
            'fields': ('bio',)
        }),
        ('Статистика', {
            'fields': ('rating', 'reviews_count'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'user', 'rating', 'title', 'visit_date', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_anonymous', 'created_at']
    search_fields = ['doctor__first_name', 'doctor__last_name', 'user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('doctor', 'user', 'rating', 'title', 'comment')
        }),
        ('Дополнительно', {
            'fields': ('visit_date', 'is_anonymous', 'is_verified')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FacilityReview)
class FacilityReviewAdmin(admin.ModelAdmin):
    list_display = ['facility', 'user', 'rating', 'title', 'visit_date', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_anonymous', 'created_at']
    search_fields = ['facility__name', 'user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('facility', 'user', 'rating', 'title', 'comment')
        }),
        ('Дополнительно', {
            'fields': ('visit_date', 'is_anonymous', 'is_verified')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )