from django.contrib import admin
from django.utils.html import format_html
from .models import ForumCategory, Topic, Post, TopicLike, PostLike, ForumNotification, TopicSubscription, CategorySubscription


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_display', 'color_display', 'order', 'get_topics_count', 'get_posts_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Внешний вид', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Статистика', {
            'fields': ('get_topics_count', 'get_posts_count'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['get_topics_count', 'get_posts_count', 'created_at', 'updated_at']
    
    def icon_display(self, obj):
        return format_html('<i class="bi {}"></i> {}', obj.icon, obj.icon)
    icon_display.short_description = 'Иконка'
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px; border: 1px solid #ccc;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Цвет'
    
    def get_topics_count(self, obj):
        return obj.get_topics_count()
    get_topics_count.short_description = 'Количество тем'
    
    def get_posts_count(self, obj):
        return obj.get_posts_count()
    get_posts_count.short_description = 'Количество сообщений'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_pinned', 'views_count', 'get_posts_count', 'likes_count', 'created_at']
    list_filter = ['status', 'is_pinned', 'is_active', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username', 'author__first_name', 'author__last_name']
    list_editable = ['status', 'is_pinned']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'category', 'author', 'family')
        }),
        ('Статус и настройки', {
            'fields': ('status', 'is_pinned', 'is_active')
        }),
        ('Статистика', {
            'fields': ('views_count', 'get_posts_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['views_count', 'get_posts_count', 'likes_count', 'created_at', 'updated_at', 'last_activity']
    raw_id_fields = ['author', 'family']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author').prefetch_related('posts')
    
    def get_posts_count(self, obj):
        return obj.get_posts_count()
    get_posts_count.short_description = 'Количество сообщений'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'topic', 'author', 'is_solution', 'likes_count', 'created_at']
    list_filter = ['is_solution', 'created_at', 'topic__category']
    search_fields = ['content', 'author__username', 'topic__title']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'author', 'content')
        }),
        ('Настройки', {
            'fields': ('is_solution',)
        }),
        ('Статистика', {
            'fields': ('likes_count',),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['likes_count', 'created_at', 'updated_at']
    raw_id_fields = ['topic', 'author']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержание'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('topic', 'author')


@admin.register(TopicLike)
class TopicLikeAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['topic__title', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'user')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    raw_id_fields = ['topic', 'user']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__content', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('post', 'user')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    raw_id_fields = ['post', 'user']


@admin.register(ForumNotification)
class ForumNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'topic', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'topic__title']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'notification_type', 'topic', 'post')
        }),
        ('Статус', {
            'fields': ('is_read',)
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'topic', 'post']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} уведомлений отмечено как прочитанные.')
    mark_as_read.short_description = 'Отметить как прочитанные'
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} уведомлений отмечено как непрочитанные.')
    mark_as_unread.short_description = 'Отметить как непрочитанные'


@admin.register(TopicSubscription)
class TopicSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'topic__category']
    search_fields = ['user__username', 'topic__title']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'topic', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'topic']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} подписок активировано.')
    activate_subscriptions.short_description = 'Активировать подписки'
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} подписок деактивировано.')
    deactivate_subscriptions.short_description = 'Деактивировать подписки'


@admin.register(CategorySubscription)
class CategorySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'category']
    search_fields = ['user__username', 'category__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'category', 'is_active')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'category']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} подписок активировано.')
    activate_subscriptions.short_description = 'Активировать подписки'
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} подписок деактивировано.')
    deactivate_subscriptions.short_description = 'Деактивировать подписки'