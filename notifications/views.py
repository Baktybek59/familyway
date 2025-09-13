from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Notification, NotificationSettings
from .services import NotificationService


@login_required
def notification_list(request):
    """Список уведомлений пользователя"""
    # Получаем все уведомления пользователя
    notifications = Notification.objects.filter(recipient=request.user)
    
    # Фильтрация
    notification_type = request.GET.get('type')
    is_read = request.GET.get('read')
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        notifications = notifications.filter(is_read=is_read_bool)
    
    # Статистика (до пагинации)
    total_count = notifications.count()
    unread_count = notifications.filter(is_read=False).count()
    
    # Пагинация
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Типы уведомлений для фильтра
    from .models import NotificationType
    notification_types = NotificationType.choices
    
    return render(request, 'notifications/list.html', {
        'page_obj': page_obj,
        'notifications': page_obj,
        'total_count': total_count,
        'unread_count': unread_count,
        'notification_types': notification_types,
        'current_type': notification_type,
        'current_read': is_read,
    })


@login_required
def notification_detail(request, notification_id):
    """Детальный просмотр уведомления"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    # Отмечаем как прочитанное
    if not notification.is_read:
        notification.mark_as_read()
    
    return render(request, 'notifications/detail.html', {
        'notification': notification,
    })


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    success = NotificationService.mark_as_read(notification_id, request.user)
    
    if success:
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Уведомление не найдено'}, status=404)


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Отметить все уведомления как прочитанные"""
    count = NotificationService.mark_all_as_read(request.user)
    return JsonResponse({'status': 'success', 'count': count})


@login_required
def notification_settings(request):
    """Настройки уведомлений"""
    settings_obj, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Обновляем настройки
        settings_obj.email_enabled = request.POST.get('email_enabled') == 'on'
        settings_obj.email_consultations = request.POST.get('email_consultations') == 'on'
        settings_obj.email_forum = request.POST.get('email_forum') == 'on'
        settings_obj.email_reviews = request.POST.get('email_reviews') == 'on'
        settings_obj.email_blog = request.POST.get('email_blog') == 'on'
        settings_obj.email_system = request.POST.get('email_system') == 'on'
        settings_obj.email_tracker = request.POST.get('email_tracker') == 'on'
        
        settings_obj.push_enabled = request.POST.get('push_enabled') == 'on'
        settings_obj.push_consultations = request.POST.get('push_consultations') == 'on'
        settings_obj.push_forum = request.POST.get('push_forum') == 'on'
        settings_obj.push_reviews = request.POST.get('push_reviews') == 'on'
        settings_obj.push_blog = request.POST.get('push_blog') == 'on'
        settings_obj.push_system = request.POST.get('push_system') == 'on'
        settings_obj.push_tracker = request.POST.get('push_tracker') == 'on'
        
        settings_obj.digest_frequency = request.POST.get('digest_frequency', 'immediate')
        settings_obj.save()
        
        return JsonResponse({'status': 'success', 'message': 'Настройки сохранены'})
    
    return render(request, 'notifications/settings.html', {
        'settings': settings_obj,
    })


@login_required
def notification_count(request):
    """Получить количество непрочитанных уведомлений (API)"""
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'count': count})


@login_required
def notification_dropdown(request):
    """Получить уведомления для выпадающего списка (API)"""
    notifications = NotificationService.get_user_notifications(request.user, limit=10)
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%d.%m.%Y %H:%M'),
            'priority': notification.priority,
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': NotificationService.get_unread_count(request.user)
    })