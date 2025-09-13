from django.contrib import admin
from .models import BlogPost, BlogComment, BlogLike


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'language', 'is_published', 'views', 'created_at']
    list_filter = ['category', 'language', 'is_published', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'title', 'content', 'category', 'language')
        }),
        ('Публикация', {
            'fields': ('is_published', 'views')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'post__category']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_approved']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('post', 'author', 'content')
        }),
        ('Модерация', {
            'fields': ('is_approved',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at', 'post__category']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
