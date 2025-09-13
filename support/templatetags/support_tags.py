from django import template

register = template.Library()

@register.filter
def is_support_staff(user):
    """Проверяет, является ли пользователь сотрудником техподдержки"""
    if not user or not user.is_authenticated:
        return False
    return hasattr(user, 'supportprofile') and user.supportprofile.is_active



