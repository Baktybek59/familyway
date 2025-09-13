from django.shortcuts import redirect
from django.urls import reverse


def get_user_redirect_url(user):
    """Определяет URL для перенаправления пользователя после авторизации"""
    
    if not user.is_authenticated:
        return None
    
    # Сотрудники техподдержки
    if hasattr(user, 'supportprofile') and user.supportprofile.is_active:
        return reverse('support:dashboard')
    
    # Писатели
    if hasattr(user, 'parent_profile') and user.parent_profile.is_writer:
        return reverse('writer:dashboard')
    
    # Обычные пользователи (родители) - остаются на главной странице
    # Не перенаправляем их, пусть остаются на главной
    
    # По умолчанию на главную
    return None
