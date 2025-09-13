from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, writer_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.ParentRegistrationView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('family/connect/', views.family_connect_view, name='family_connect'),
    path('family/disconnect/', views.family_disconnect_view, name='family_disconnect'),
    path('family/', views.family_management_view, name='family_management'),
    path('family/add-child/', views.add_child_view, name='add_child'),
    path('family/edit-child/<int:child_id>/', views.edit_child_view, name='edit_child'),
    path('family/delete-child/<int:child_id>/', views.delete_child_view, name='delete_child'),
    path('child/<int:child_id>/', views.child_detail_view, name='child_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # Writer URLs
    path('writer/login/', writer_views.writer_login, name='writer_login'),
    path('writer/dashboard/', writer_views.writer_dashboard, name='writer_dashboard'),
    path('writer/articles/', writer_views.writer_articles, name='writer_articles'),
    path('writer/article/create/', writer_views.writer_article_create, name='writer_article_create'),
    path('writer/article/edit/<int:article_id>/', writer_views.writer_article_edit, name='writer_article_edit'),
    path('writer/analytics/', writer_views.writer_analytics, name='writer_analytics'),
    path('writer/profile/edit/', writer_views.writer_profile_edit, name='writer_profile_edit'),
    path('writer/password/change/', writer_views.writer_password_change, name='writer_password_change'),
    
    # Writer Application URLs
    path('writer/application/', views.writer_application_create, name='writer_application'),
    path('writer/application/success/<int:application_id>/', views.writer_application_success, name='writer_application_success'),
]
