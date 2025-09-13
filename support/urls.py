from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Дашборд
    path('', views.SupportDashboardView.as_view(), name='dashboard'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
    
    # Тикеты
    path('tickets/', views.SupportDashboardView.as_view(), name='ticket_list'),
    path('tickets/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/dispute/', views.DisputeTicketCreateView.as_view(), name='dispute_ticket_create'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:ticket_id>/comment/', views.add_comment, name='add_comment'),
    path('tickets/<int:ticket_id>/assign/', views.assign_ticket, name='assign_ticket'),
    
    # Заявки учреждений
    path('facility-requests/', views.facility_requests, name='facility_requests'),
    path('facility-requests/<int:request_id>/', views.facility_request_detail, name='facility_request_detail'),
    
    # Модерация форума
    path('forum/', views.forum_moderation, name='forum_moderation'),
    path('forum/posts/<int:post_id>/approve/', views.approve_forum_post, name='approve_forum_post'),
    path('forum/posts/<int:post_id>/delete/', views.delete_forum_post, name='delete_forum_post'),
    path('forum/posts/<int:post_id>/edit/', views.edit_forum_post, name='edit_forum_post'),
    path('forum/topics/<int:topic_id>/delete/', views.delete_forum_topic, name='delete_forum_topic'),
    path('forum/topics/<int:topic_id>/edit/', views.edit_forum_topic, name='edit_forum_topic'),
    
    # Одобрение блога
    path('blog/', views.blog_approval, name='blog_approval'),
    path('blog/posts/<int:post_id>/approve/', views.approve_blog_post, name='approve_blog_post'),
    path('blog/posts/<int:post_id>/edit/', views.edit_blog_post, name='edit_blog_post'),
    path('blog/posts/<int:post_id>/delete/', views.delete_blog_post, name='delete_blog_post'),
    path('blog/creators/', views.blog_creators, name='blog_creators'),
    
    # Модерация отзывов
    path('reviews/', views.review_moderation, name='review_moderation'),
    path('reviews/<int:review_id>/approve/', views.approve_review, name='approve_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    
    # Уведомления
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Профиль
    path('profile/', views.support_profile, name='profile'),
    path('profile/edit/', views.support_profile_edit, name='profile_edit'),
    
    # Уведомления об удалении отзывов
    path('review-deletion-notifications/', views.review_deletion_notifications, name='review_deletion_notifications'),
    
    # Заявки писателей
    path('writer-applications/', views.writer_applications, name='writer_applications'),
    path('writer-applications/<int:application_id>/', views.writer_application_detail, name='writer_application_detail'),
    path('writer-applications/approved/', views.writer_applications_approved, name='writer_applications_approved'),
    path('writer-applications/rejected/', views.writer_applications_rejected, name='writer_applications_rejected'),
]
