from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Главная страница форума
    path('', views.ForumIndexView.as_view(), name='index'),
    
    # Категории
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Темы
    path('topic/<int:pk>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('topic/create/', views.TopicCreateView.as_view(), name='topic_create'),
    path('topic/<int:pk>/edit/', views.TopicUpdateView.as_view(), name='topic_edit'),
    path('topic/<int:pk>/delete/', views.TopicDeleteView.as_view(), name='topic_delete'),
    
    # Сообщения
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # AJAX действия
    path('topic/<int:pk>/like/', views.like_topic, name='like_topic'),
    path('topic/<int:pk>/dislike/', views.dislike_topic, name='dislike_topic'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/dislike/', views.dislike_post, name='dislike_post'),
    path('post/<int:pk>/solution/', views.mark_solution, name='mark_solution'),
    
    # Подписки
    path('topic/<int:pk>/subscribe/', views.subscribe_to_topic, name='subscribe_topic'),
    path('topic/<int:pk>/unsubscribe/', views.unsubscribe_from_topic, name='unsubscribe_topic'),
    path('category/<int:pk>/subscribe/', views.subscribe_to_category, name='subscribe_category'),
    path('category/<int:pk>/unsubscribe/', views.unsubscribe_from_category, name='unsubscribe_category'),
    path('subscription/<int:pk>/<str:type>/status/', views.get_subscription_status, name='subscription_status'),
    
    # Поиск
    path('search/', views.search_topics, name='search'),
]
