from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.tracker_dashboard, name='dashboard'),
    
    # Growth URLs
    path('growth/', views.GrowthListView.as_view(), name='growth_list'),
    path('growth/add/', views.GrowthCreateView.as_view(), name='growth_create'),
    path('growth/<int:pk>/edit/', views.GrowthUpdateView.as_view(), name='growth_update'),
    path('growth/<int:pk>/delete/', views.GrowthDeleteView.as_view(), name='growth_delete'),
    
    # Sleep URLs
    path('sleep/', views.SleepListView.as_view(), name='sleep_list'),
    path('sleep/add/', views.SleepCreateView.as_view(), name='sleep_create'),
    path('sleep/<int:pk>/edit/', views.SleepUpdateView.as_view(), name='sleep_update'),
    path('sleep/<int:pk>/delete/', views.SleepDeleteView.as_view(), name='sleep_delete'),
    
    # Cry URLs
    path('cry/', views.CryListView.as_view(), name='cry_list'),
    path('cry/add/', views.CryCreateView.as_view(), name='cry_create'),
    path('cry/<int:pk>/edit/', views.CryUpdateView.as_view(), name='cry_update'),
    path('cry/<int:pk>/delete/', views.CryDeleteView.as_view(), name='cry_delete'),
    
    # Feeding URLs
    path('feeding/', views.FeedingListView.as_view(), name='feeding_list'),
    path('feeding/add/', views.FeedingCreateView.as_view(), name='feeding_create'),
    path('feeding/<int:pk>/edit/', views.FeedingUpdateView.as_view(), name='feeding_update'),
    path('feeding/<int:pk>/delete/', views.FeedingDeleteView.as_view(), name='feeding_delete'),
    
    # Vaccination URLs
    path('vaccination/', views.VaccinationListView.as_view(), name='vaccination_list'),
    path('vaccination/add/', views.VaccinationCreateView.as_view(), name='vaccination_create'),
    path('vaccination/<int:pk>/edit/', views.VaccinationUpdateView.as_view(), name='vaccination_update'),
    path('vaccination/<int:pk>/delete/', views.VaccinationDeleteView.as_view(), name='vaccination_delete'),
]

