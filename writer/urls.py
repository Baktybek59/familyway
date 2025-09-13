from django.urls import path
from . import views

app_name = 'writer'

urlpatterns = [
    path('dashboard/', views.writer_dashboard, name='dashboard'),
    path('profile/edit/', views.writer_profile_edit, name='profile_edit'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
]
