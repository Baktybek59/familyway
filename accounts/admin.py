from django.contrib import admin
from .models import ParentProfile, Family, Child


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'name')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'role', 'phone_number', 'city', 'workplace', 'family', 'family_code']
    list_filter = ['user_type', 'role', 'city', 'family']
    search_fields = ['user__username', 'user__email', 'phone_number', 'city', 'workplace', 'family_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'user_type', 'role')
        }),
        ('Личная информация', {
            'fields': ('phone_number', 'birth_date', 'city', 'workplace')
        }),
        ('Информация о ребенке', {
            'fields': ('child_name', 'child_birth_date')
        }),
        ('Семья', {
            'fields': ('family', 'family_code')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'gender', 'birth_date', 'age_display', 'created_at']
    list_filter = ['gender', 'family', 'created_at']
    search_fields = ['name', 'family__name']
    readonly_fields = ['created_at', 'updated_at', 'age_display']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('family', 'name', 'birth_date', 'gender')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at', 'age_display'),
            'classes': ('collapse',)
        }),
    )
    
    def age_display(self, obj):
        return f"{obj.age_years} лет, {obj.age_months} месяцев"
    age_display.short_description = 'Возраст'
