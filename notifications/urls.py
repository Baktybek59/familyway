from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Список уведомлений
    path('', views.notification_list, name='list'),
    path('settings/', views.notification_settings, name='settings'),
    
    # API для уведомлений
    path('api/count/', views.notification_count, name='api_count'),
    path('api/dropdown/', views.notification_dropdown, name='api_dropdown'),
    path('api/mark-all-read/', views.mark_all_as_read, name='api_mark_all_read'),
    
    # Детальный просмотр и действия
    path('<int:notification_id>/', views.notification_detail, name='detail'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_read'),
]




