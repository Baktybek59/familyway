from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from accounts.models import Family


class ForumCategory(models.Model):
    """Категория форума"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    icon = models.CharField(max_length=50, default='bi-chat-dots', verbose_name=_('Иконка'))
    color = models.CharField(max_length=7, default='#007bff', verbose_name=_('Цвет'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Категория форума')
        verbose_name_plural = _('Категории форума')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forum:category_detail', kwargs={'pk': self.pk})

    def get_topics_count(self):
        return self.topics.filter(is_active=True).count()

    def get_posts_count(self):
        return sum(topic.posts.count() for topic in self.topics.filter(is_active=True))


class Topic(models.Model):
    """Тема обсуждения"""
    STATUS_CHOICES = [
        ('open', _('Открыта')),
        ('closed', _('Закрыта')),
        ('pinned', _('Закреплена')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='topics', verbose_name=_('Категория'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics', verbose_name=_('Автор'))
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_topics', verbose_name=_('Семья'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name=_('Статус'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    is_pinned = models.BooleanField(default=False, verbose_name=_('Закреплена'))
    is_locked = models.BooleanField(default=False, verbose_name=_('Заблокирована'))
    is_announcement = models.BooleanField(default=False, verbose_name=_('Объявление'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))
    likes_count = models.PositiveIntegerField(default=0, verbose_name=_('Лайки'))
    posts_count = models.PositiveIntegerField(default=0, verbose_name=_('Сообщения'))
    tags = models.CharField(max_length=500, blank=True, verbose_name=_('Теги'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now_add=True)
    last_post = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_post_topics', verbose_name=_('Последнее сообщение'))

    class Meta:
        verbose_name = _('Тема')
        verbose_name_plural = _('Темы')
        ordering = ['-is_pinned', '-last_activity']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.pk})

    def get_posts_count(self):
        return self.posts.count()

    def get_last_post(self):
        return self.posts.order_by('-created_at').first()

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_dislikes_count(self):
        return self.dislikes.count()
    
    def is_disliked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.dislikes.filter(user=user).exists()
    
    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags_list):
        """Устанавливает теги из списка"""
        self.tags = ', '.join(tags_list)
    
    def update_posts_count(self):
        """Обновляет счетчик сообщений"""
        self.posts_count = self.posts.count()
        self.save(update_fields=['posts_count'])
    
    def update_last_post(self):
        """Обновляет последнее сообщение"""
        last_post = self.posts.order_by('-created_at').first()
        self.last_post = last_post
        self.last_activity = last_post.created_at if last_post else self.created_at
        self.save(update_fields=['last_post', 'last_activity'])
    
    def can_user_post(self, user):
        """Проверяет, может ли пользователь писать в теме"""
        if not user.is_authenticated:
            return False
        if self.is_locked:
            return False
        if self.status == 'closed':
            return False
        return True


class Post(models.Model):
    """Сообщение в теме"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Тема'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts', verbose_name=_('Автор'))
    content = models.TextField(verbose_name=_('Содержание'))
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name=_('Ответ на сообщение'))
    is_solution = models.BooleanField(default=False, verbose_name=_('Решение'))
    likes_count = models.PositiveIntegerField(default=0, verbose_name=_('Лайки'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Сообщение')
        verbose_name_plural = _('Сообщения')
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение в теме '{self.topic.title}' от {self.author.username}"

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.topic.pk}) + f'#post-{self.pk}'
    
    def get_dislikes_count(self):
        return self.dislikes.count()
    
    def is_disliked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.dislikes.filter(user=user).exists()
    
    def get_replies_count(self):
        return self.replies.count()
    
    def is_reply(self):
        return self.parent_post is not None


class TopicLike(models.Model):
    """Лайк темы"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Тема'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topic_likes', verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Лайк темы')
        verbose_name_plural = _('Лайки тем')
        unique_together = ['topic', 'user']

    def __str__(self):
        return f"Лайк темы '{self.topic.title}' от {self.user.username}"


class PostLike(models.Model):
    """Лайк сообщения"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Сообщение'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Лайк сообщения')
        verbose_name_plural = _('Лайки сообщений')
        unique_together = ['post', 'user']

    def __str__(self):
        return f"Лайк сообщения от {self.user.username}"


class TopicDislike(models.Model):
    """Дизлайк темы"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='dislikes', verbose_name=_('Тема'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topic_dislikes', verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Дизлайк темы')
        verbose_name_plural = _('Дизлайки тем')
        unique_together = ['topic', 'user']

    def __str__(self):
        return f"Дизлайк темы '{self.topic.title}' от {self.user.username}"


class PostDislike(models.Model):
    """Дизлайк сообщения"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes', verbose_name=_('Сообщение'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_dislikes', verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Дизлайк сообщения')
        verbose_name_plural = _('Дизлайки сообщений')
        unique_together = ['post', 'user']

    def __str__(self):
        return f"Дизлайк сообщения от {self.user.username}"


class ForumNotification(models.Model):
    """Уведомление форума"""
    TYPE_CHOICES = [
        ('new_post', _('Новое сообщение')),
        ('topic_liked', _('Тема понравилась')),
        ('post_liked', _('Сообщение понравилось')),
        ('solution_marked', _('Отмечено как решение')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_notifications', verbose_name=_('Пользователь'))
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_('Тип уведомления'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name=_('Тема'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name=_('Сообщение'))
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Уведомление форума')
        verbose_name_plural = _('Уведомления форума')
        ordering = ['-created_at']

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.get_notification_type_display()}"


class TopicSubscription(models.Model):
    """Подписка на тему форума"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topic_subscriptions', verbose_name=_('Пользователь'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subscribers', verbose_name=_('Тема'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подписки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))

    class Meta:
        verbose_name = _('Подписка на тему')
        verbose_name_plural = _('Подписки на темы')
        unique_together = ['user', 'topic']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} подписан на тему '{self.topic.title}'"


class CategorySubscription(models.Model):
    """Подписка на категорию форума"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions', verbose_name=_('Пользователь'))
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='subscribers', verbose_name=_('Категория'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подписки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))

    class Meta:
        verbose_name = _('Подписка на категорию')
        verbose_name_plural = _('Подписки на категории')
        unique_together = ['user', 'category']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} подписан на категорию '{self.category.name}'"


class UserReputation(models.Model):
    """Репутация пользователя на форуме"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_reputation', verbose_name=_('Пользователь'))
    points = models.IntegerField(default=0, verbose_name=_('Очки репутации'))
    level = models.PositiveIntegerField(default=1, verbose_name=_('Уровень'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Репутация пользователя')
        verbose_name_plural = _('Репутация пользователей')

    def __str__(self):
        return f"Репутация {self.user.username}: {self.points} очков"

    def update_level(self):
        """Обновляет уровень пользователя на основе очков"""
        if self.points >= 1000:
            self.level = 5
        elif self.points >= 500:
            self.level = 4
        elif self.points >= 200:
            self.level = 3
        elif self.points >= 50:
            self.level = 2
        else:
            self.level = 1
        self.save(update_fields=['level'])


class ReputationAction(models.Model):
    """Действие, влияющее на репутацию"""
    ACTION_CHOICES = [
        ('post_liked', _('Лайк за сообщение')),
        ('post_disliked', _('Дизлайк за сообщение')),
        ('topic_liked', _('Лайк за тему')),
        ('topic_disliked', _('Дизлайк за тему')),
        ('solution_marked', _('Отмечено как решение')),
        ('helpful_post', _('Полезное сообщение')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reputation_actions', verbose_name=_('Пользователь'))
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_('Тип действия'))
    points = models.IntegerField(verbose_name=_('Очки'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Тема'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Сообщение'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Действие репутации')
        verbose_name_plural = _('Действия репутации')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.get_action_type_display()} ({self.points:+d})"


class ForumModeration(models.Model):
    """Модерация форума"""
    ACTION_CHOICES = [
        ('topic_locked', _('Тема заблокирована')),
        ('topic_unlocked', _('Тема разблокирована')),
        ('topic_pinned', _('Тема закреплена')),
        ('topic_unpinned', _('Тема откреплена')),
        ('topic_closed', _('Тема закрыта')),
        ('topic_opened', _('Тема открыта')),
        ('post_hidden', _('Сообщение скрыто')),
        ('post_shown', _('Сообщение показано')),
        ('user_warned', _('Пользователь предупрежден')),
        ('user_banned', _('Пользователь забанен')),
    ]

    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions', verbose_name=_('Модератор'))
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_('Тип действия'))
    reason = models.TextField(blank=True, verbose_name=_('Причина'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Тема'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Сообщение'))
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='moderation_target', verbose_name=_('Целевой пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Действие модерации')
        verbose_name_plural = _('Действия модерации')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moderator.username}: {self.get_action_type_display()}"


class ForumPoll(models.Model):
    """Опросы в темах"""
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='poll', verbose_name=_('Тема'))
    question = models.CharField(max_length=200, verbose_name=_('Вопрос'))
    is_multiple_choice = models.BooleanField(default=False, verbose_name=_('Множественный выбор'))
    is_anonymous = models.BooleanField(default=False, verbose_name=_('Анонимный'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Истекает'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Опрос')
        verbose_name_plural = _('Опросы')

    def __str__(self):
        return f"Опрос: {self.question}"

    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class PollOption(models.Model):
    """Варианты ответов в опросе"""
    poll = models.ForeignKey(ForumPoll, on_delete=models.CASCADE, related_name='options', verbose_name=_('Опрос'))
    text = models.CharField(max_length=100, verbose_name=_('Текст варианта'))
    votes_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество голосов'))

    class Meta:
        verbose_name = _('Вариант ответа')
        verbose_name_plural = _('Варианты ответов')
        ordering = ['id']

    def __str__(self):
        return f"{self.poll.question}: {self.text}"


class PollVote(models.Model):
    """Голоса в опросе"""
    poll = models.ForeignKey(ForumPoll, on_delete=models.CASCADE, related_name='votes', verbose_name=_('Опрос'))
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes', verbose_name=_('Вариант'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes', verbose_name=_('Пользователь'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Голос')
        verbose_name_plural = _('Голоса')
        unique_together = ['poll', 'user']

    def __str__(self):
        return f"{self.user.username} голосовал за '{self.option.text}'"