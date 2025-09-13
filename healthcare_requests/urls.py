from django.urls import path
from . import views

app_name = 'healthcare_requests'

urlpatterns = [
    # Публичные страницы
    path('request/', views.facility_request_create, name='request_create'),
    path('request/success/<int:request_id>/', views.facility_request_success, name='request_success'),
    path('login/', views.facility_login, name='facility_login'),
    
    # Дашборд учреждения
    path('dashboard/', views.facility_dashboard, name='facility_dashboard'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Управление учреждением
    path('doctors/', views.facility_doctors, name='facility_doctors'),
    path('consultations/', views.facility_consultations, name='facility_consultations'),
    path('analytics/', views.facility_analytics, name='facility_analytics'),
    path('notifications/', views.facility_notifications, name='facility_notifications'),
    
    # Админские страницы
    path('admin/requests/', views.admin_request_list, name='admin_request_list'),
    path('admin/requests/<int:request_id>/', views.admin_request_detail, name='admin_request_detail'),
]
