from django.urls import path
from . import views

app_name = 'healthcare'

urlpatterns = [
    # Main pages
    path('', views.HealthcareIndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.HealthcareCategoryView.as_view(), name='category'),
    
    # Facilities
    path('facility/<int:pk>/', views.HealthcareFacilityDetailView.as_view(), name='facility_detail'),
    path('facility/add/', views.HealthcareFacilityCreateView.as_view(), name='facility_add'),
    path('facility/<int:facility_id>/review/', views.add_facility_review, name='add_facility_review'),
    
    # Doctors
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctor/add/', views.DoctorCreateView.as_view(), name='doctor_add'),
    path('doctor/<int:doctor_id>/review/', views.add_doctor_review, name='add_doctor_review'),
    
    # Doctor authentication
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/consultations/', views.doctor_consultations, name='doctor_consultations'),
    path('doctor/consultation/<int:consultation_id>/', views.doctor_consultation_detail, name='doctor_consultation_detail'),
    path('doctor/profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('doctor/password/change/', views.doctor_password_change, name='doctor_password_change'),
]
