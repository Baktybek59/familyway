from django.urls import path
from . import views

app_name = 'consultant'

urlpatterns = [
    # Консультанты
    path('', views.ConsultantListView.as_view(), name='consultant_list'),
    path('consultant/<int:pk>/', views.ConsultantDetailView.as_view(), name='consultant_detail'),
    path('consultant/profile/edit/', views.consultant_profile_edit, name='consultant_profile_edit'),
    path('consultant/dashboard/', views.consultant_dashboard, name='consultant_dashboard'),
    
    # Консультации
    path('consultations/', views.ConsultationListView.as_view(), name='consultation_list'),
    path('consultations/create/', views.ConsultationCreateView.as_view(), name='consultation_create'),
    path('consultations/<int:pk>/', views.ConsultationDetailView.as_view(), name='consultation_detail'),
    path('consultations/<int:consultation_id>/message/', views.send_message, name='send_message'),
    path('consultations/<int:consultation_id>/review/', views.add_review, name='add_review'),
    path('consultations/<int:consultation_id>/complete/', views.mark_consultation_completed, name='mark_completed'),
]

