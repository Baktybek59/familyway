from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import ForumCategory, Topic, Post, TopicLike, PostLike, TopicDislike, PostDislike, ForumNotification, TopicSubscription, CategorySubscription
from .forms import TopicForm, PostForm, TopicSearchForm
from accounts.models import ParentProfile


class ForumIndexView(ListView):
    """Главная страница форума - список категорий"""
    model = ForumCategory
    template_name = 'forum/index.html'
    context_object_name = 'categories'
    paginate_by = 12

    def get_queryset(self):
        return ForumCategory.objects.filter(is_active=True).annotate(
            topics_count=Count('topics', filter=Q(topics__is_active=True)),
            posts_count=Count('topics__posts', filter=Q(topics__is_active=True))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Статистика форума
        context['total_topics'] = Topic.objects.filter(is_active=True).count()
        context['total_posts'] = Post.objects.count()
        context['recent_topics'] = Topic.objects.filter(is_active=True).order_by('-created_at')[:5]
        return context


class CategoryDetailView(ListView):
    """Детальная страница категории - список тем"""
    model = Topic
    template_name = 'forum/category_detail.html'
    context_object_name = 'topics'
    paginate_by = 20

    def get_queryset(self):
        self.category = get_object_or_404(ForumCategory, pk=self.kwargs['pk'], is_active=True)
        queryset = Topic.objects.filter(
            category=self.category,
            is_active=True
        ).select_related('author', 'category').prefetch_related('posts').order_by('-is_pinned', '-last_activity')

        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            if status == 'pinned':
                queryset = queryset.filter(is_pinned=True)
            else:
                queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['search_form'] = TopicSearchForm(self.request.GET)
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class TopicDetailView(DetailView):
    """Детальная страница темы"""
    model = Topic
    template_name = 'forum/topic_detail.html'
    context_object_name = 'topic'

    def get_queryset(self):
        return Topic.objects.filter(is_active=True).select_related(
            'author', 'category'
        ).prefetch_related('posts__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        
        # Увеличиваем счетчик просмотров
        topic.increment_views()
        
        # Получаем сообщения с пагинацией
        posts = topic.posts.all().order_by('created_at')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['posts'] = paginator.get_page(page_number)
        
        # Форма для нового сообщения (только для авторизованных)
        if self.request.user.is_authenticated:
            context['post_form'] = PostForm()
        else:
            context['post_form'] = None
        
        # Информация о лайках и дизлайках темы
        context['topic_likes_count'] = topic.likes.count()
        context['topic_dislikes_count'] = topic.get_dislikes_count()
        context['is_topic_liked'] = topic.likes.filter(user=self.request.user).exists() if self.request.user.is_authenticated else False
        context['is_topic_disliked'] = topic.is_disliked_by(self.request.user) if self.request.user.is_authenticated else False
        
        # Проверяем, может ли пользователь создавать сообщения
        context['can_post'] = topic.can_user_post(self.request.user)
        
        # Информация о тегах
        context['topic_tags'] = topic.get_tags_list()
        
        # Информация об опросе
        if hasattr(topic, 'poll'):
            context['poll'] = topic.poll
            if self.request.user.is_authenticated:
                context['user_voted'] = topic.poll.votes.filter(user=self.request.user).exists()
            else:
                context['user_voted'] = False
        
        # Информация о репутации автора
        if self.request.user.is_authenticated:
            context['user_reputation'] = getattr(self.request.user, 'forum_reputation', None)
        
        return context

    def post(self, request, *args, **kwargs):
        """Обработка создания нового сообщения"""
        if not request.user.is_authenticated:
            messages.error(request, _('Необходимо войти в систему для создания сообщений.'))
            return redirect('accounts:login')
        
        topic = self.get_object()
        form = PostForm(request.POST)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            
            # Проверяем, что родительский пост принадлежит той же теме
            if post.parent_post and post.parent_post.topic != topic:
                messages.error(request, _('Нельзя отвечать на сообщение из другой темы.'))
                return redirect('forum:topic_detail', pk=topic.pk)
            
            post.save()
            
            # Обновляем счетчики темы
            topic.update_posts_count()
            topic.update_last_post()
            
            # Отправляем уведомления подписчикам темы
            from notifications.services import NotificationService
            NotificationService.send_forum_topic_reply_notification(topic, post, request.user)
            
            # Отправляем уведомления о цитировании
            from .utils import extract_quoted_users_from_content
            quoted_users = extract_quoted_users_from_content(post.content)
            for quoted_user in quoted_users:
                NotificationService.send_forum_post_quoted_notification(
                    quoted_user=quoted_user,
                    topic=topic,
                    post=post,
                    sender=request.user
                )
            
            messages.success(request, _('Сообщение успешно добавлено!'))
            return redirect('forum:topic_detail', pk=topic.pk)
        else:
            messages.error(request, _('Ошибка при создании сообщения.'))
            return redirect('forum:topic_detail', pk=topic.pk)


class TopicCreateView(LoginRequiredMixin, CreateView):
    """Создание новой темы"""
    model = Topic
    form_class = TopicForm
    template_name = 'forum/topic_create.html'

    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.author = self.request.user
        
        # Получаем семью пользователя, если есть
        try:
            parent_profile = self.request.user.parent_profile
            topic.family = parent_profile.family
        except ParentProfile.DoesNotExist:
            pass
        
        topic.save()
        
        # Инициализируем счетчики
        topic.update_posts_count()
        topic.update_last_post()
        
        # Обрабатываем теги
        tags_text = form.cleaned_data.get('tags', '')
        if tags_text:
            tags_list = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            topic.set_tags(tags_list)
        
        # Отправляем уведомления подписчикам категории
        from notifications.services import NotificationService
        NotificationService.send_forum_topic_created_notification(topic, self.request.user)
        
        messages.success(self.request, _('Тема успешно создана!'))
        return redirect('forum:topic_detail', pk=topic.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ForumCategory.objects.filter(is_active=True)
        return context


class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование темы"""
    model = Topic
    form_class = TopicForm
    template_name = 'forum/topic_edit.html'

    def test_func(self):
        topic = self.get_object()
        return self.request.user == topic.author or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, _('Тема успешно обновлена!'))
        return super().form_valid(form)


class TopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление темы"""
    model = Topic
    template_name = 'forum/topic_confirm_delete.html'
    success_url = reverse_lazy('forum:index')

    def test_func(self):
        topic = self.get_object()
        return self.request.user == topic.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        topic = self.get_object()
        topic.is_active = False
        topic.save()
        messages.success(request, _('Тема успешно удалена!'))
        return redirect(self.success_url)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование сообщения"""
    model = Post
    form_class = PostForm
    template_name = 'forum/post_edit.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, _('Сообщение успешно обновлено!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.object.topic.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление сообщения"""
    model = Post
    template_name = 'forum/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff

    def get_success_url(self):
        return reverse('forum:topic_detail', kwargs={'pk': self.object.topic.pk})

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        topic = post.topic
        post.delete()
        messages.success(request, _('Сообщение успешно удалено!'))
        return redirect('forum:topic_detail', pk=topic.pk)


@login_required
def like_topic(request, pk):
    """Лайк/анлайк темы"""
    topic = get_object_or_404(Topic, pk=pk, is_active=True)
    
    # Удаляем дизлайк, если он есть
    TopicDislike.objects.filter(topic=topic, user=request.user).delete()
    
    like, created = TopicLike.objects.get_or_create(
        topic=topic,
        user=request.user
    )
    
    if created:
        topic.likes_count += 1
        topic.save(update_fields=['likes_count'])
        return JsonResponse({
            'status': 'liked', 
            'likes_count': topic.likes.count(),
            'dislikes_count': topic.get_dislikes_count()
        })
    else:
        like.delete()
        topic.likes_count -= 1
        topic.save(update_fields=['likes_count'])
        return JsonResponse({
            'status': 'unliked', 
            'likes_count': topic.likes.count(),
            'dislikes_count': topic.get_dislikes_count()
        })


@login_required
def like_post(request, pk):
    """Лайк/анлайк сообщения"""
    post = get_object_or_404(Post, pk=pk)
    
    # Удаляем дизлайк, если он есть
    PostDislike.objects.filter(post=post, user=request.user).delete()
    
    like, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if created:
        post.likes_count += 1
        post.save(update_fields=['likes_count'])
        return JsonResponse({
            'status': 'liked', 
            'likes_count': post.likes.count(),
            'dislikes_count': post.get_dislikes_count()
        })
    else:
        like.delete()
        post.likes_count -= 1
        post.save(update_fields=['likes_count'])
        return JsonResponse({
            'status': 'unliked', 
            'likes_count': post.likes.count(),
            'dislikes_count': post.get_dislikes_count()
        })


@login_required
def dislike_topic(request, pk):
    """Дизлайк/андизлайк темы"""
    topic = get_object_or_404(Topic, pk=pk, is_active=True)
    
    # Удаляем лайк, если он есть
    TopicLike.objects.filter(topic=topic, user=request.user).delete()
    
    dislike, created = TopicDislike.objects.get_or_create(
        topic=topic,
        user=request.user
    )
    
    if created:
        return JsonResponse({
            'status': 'disliked', 
            'likes_count': topic.likes.count(),
            'dislikes_count': topic.get_dislikes_count()
        })
    else:
        dislike.delete()
        return JsonResponse({
            'status': 'undisliked', 
            'likes_count': topic.likes.count(),
            'dislikes_count': topic.get_dislikes_count()
        })


@login_required
def dislike_post(request, pk):
    """Дизлайк/андизлайк сообщения"""
    post = get_object_or_404(Post, pk=pk)
    
    # Удаляем лайк, если он есть
    PostLike.objects.filter(post=post, user=request.user).delete()
    
    dislike, created = PostDislike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if created:
        return JsonResponse({
            'status': 'disliked', 
            'likes_count': post.likes.count(),
            'dislikes_count': post.get_dislikes_count()
        })
    else:
        dislike.delete()
        return JsonResponse({
            'status': 'undisliked', 
            'likes_count': post.likes.count(),
            'dislikes_count': post.get_dislikes_count()
        })


@login_required
def mark_solution(request, pk):
    """Отметить сообщение как решение"""
    post = get_object_or_404(Post, pk=pk)
    topic = post.topic
    
    # Проверяем, что пользователь - автор темы
    if request.user != topic.author:
        return JsonResponse({'status': 'error', 'message': 'Нет прав для выполнения действия'})
    
    # Снимаем решение с других сообщений в теме
    topic.posts.update(is_solution=False)
    
    # Отмечаем текущее сообщение как решение
    post.is_solution = True
    post.save(update_fields=['is_solution'])
    
    return JsonResponse({'status': 'success', 'message': 'Сообщение отмечено как решение'})


def search_topics(request):
    """Поиск тем"""
    form = TopicSearchForm(request.GET)
    topics = Topic.objects.filter(is_active=True).select_related('author', 'category')
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        
        if search_query:
            topics = topics.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        if category:
            topics = topics.filter(category=category)
        
        if status:
            if status == 'pinned':
                topics = topics.filter(is_pinned=True)
            else:
                topics = topics.filter(status=status)
    
    topics = topics.order_by('-is_pinned', '-last_activity')
    
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    topics = paginator.get_page(page_number)
    
    context = {
        'topics': topics,
        'form': form,
        'search_query': request.GET.get('search_query', ''),
        'current_category': request.GET.get('category', ''),
        'current_status': request.GET.get('status', ''),
    }
    
    return render(request, 'forum/search_results.html', context)


@login_required
def subscribe_to_topic(request, pk):
    """Подписаться на тему"""
    topic = get_object_or_404(Topic, pk=pk, is_active=True)
    
    subscription, created = TopicSubscription.objects.get_or_create(
        user=request.user,
        topic=topic,
        defaults={'is_active': True}
    )
    
    if created:
        return JsonResponse({'status': 'subscribed', 'message': 'Вы подписались на тему'})
    elif not subscription.is_active:
        subscription.is_active = True
        subscription.save()
        return JsonResponse({'status': 'subscribed', 'message': 'Подписка на тему активирована'})
    else:
        return JsonResponse({'status': 'already_subscribed', 'message': 'Вы уже подписаны на эту тему'})


@login_required
def unsubscribe_from_topic(request, pk):
    """Отписаться от темы"""
    topic = get_object_or_404(Topic, pk=pk, is_active=True)
    
    try:
        subscription = TopicSubscription.objects.get(user=request.user, topic=topic)
        subscription.is_active = False
        subscription.save()
        return JsonResponse({'status': 'unsubscribed', 'message': 'Вы отписались от темы'})
    except TopicSubscription.DoesNotExist:
        return JsonResponse({'status': 'not_subscribed', 'message': 'Вы не подписаны на эту тему'})


@login_required
def subscribe_to_category(request, pk):
    """Подписаться на категорию"""
    category = get_object_or_404(ForumCategory, pk=pk, is_active=True)
    
    subscription, created = CategorySubscription.objects.get_or_create(
        user=request.user,
        category=category,
        defaults={'is_active': True}
    )
    
    if created:
        return JsonResponse({'status': 'subscribed', 'message': 'Вы подписались на категорию'})
    elif not subscription.is_active:
        subscription.is_active = True
        subscription.save()
        return JsonResponse({'status': 'subscribed', 'message': 'Подписка на категорию активирована'})
    else:
        return JsonResponse({'status': 'already_subscribed', 'message': 'Вы уже подписаны на эту категорию'})


@login_required
def unsubscribe_from_category(request, pk):
    """Отписаться от категории"""
    category = get_object_or_404(ForumCategory, pk=pk, is_active=True)
    
    try:
        subscription = CategorySubscription.objects.get(user=request.user, category=category)
        subscription.is_active = False
        subscription.save()
        return JsonResponse({'status': 'unsubscribed', 'message': 'Вы отписались от категории'})
    except CategorySubscription.DoesNotExist:
        return JsonResponse({'status': 'not_subscribed', 'message': 'Вы не подписаны на эту категорию'})


@login_required
def get_subscription_status(request, pk, type):
    """Получить статус подписки"""
    if type == 'topic':
        topic = get_object_or_404(Topic, pk=pk, is_active=True)
        try:
            subscription = TopicSubscription.objects.get(user=request.user, topic=topic)
            return JsonResponse({'status': 'subscribed', 'is_active': subscription.is_active})
        except TopicSubscription.DoesNotExist:
            return JsonResponse({'status': 'not_subscribed', 'is_active': False})
    elif type == 'category':
        category = get_object_or_404(ForumCategory, pk=pk, is_active=True)
        try:
            subscription = CategorySubscription.objects.get(user=request.user, category=category)
            return JsonResponse({'status': 'subscribed', 'is_active': subscription.is_active})
        except CategorySubscription.DoesNotExist:
            return JsonResponse({'status': 'not_subscribed', 'is_active': False})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный тип подписки'})