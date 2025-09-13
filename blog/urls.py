from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('<int:pk>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('<int:pk>/like/', views.like_post, name='like_post'),
    path('<int:pk>/dislike/', views.dislike_post, name='dislike_post'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
