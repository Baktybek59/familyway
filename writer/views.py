from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q
from .models import WriterProfile, WriterDashboard
from .forms import WriterProfileForm, BlogPostForm
from blog.models import BlogPost
from accounts.models import ParentProfile


@login_required
def writer_dashboard(request):
    """Дашборд писателя"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к дашборду писателя'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    try:
        writer_profile = request.user.writer_profile
    except WriterProfile.DoesNotExist:
        # Создаем профиль писателя, если его нет
        writer_profile = WriterProfile.objects.create(user=request.user)
        WriterDashboard.objects.create(writer=writer_profile)
    
    # Получаем статистику
    total_posts = writer_profile.total_posts
    total_views = writer_profile.total_views
    recent_posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')[:5]
    
    # Обновляем дашборд
    dashboard, created = WriterDashboard.objects.get_or_create(writer=writer_profile)
    
    context = {
        'writer_profile': writer_profile,
        'dashboard': dashboard,
        'total_posts': total_posts,
        'total_views': total_views,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'writer/dashboard.html', context)


@login_required
def writer_profile_edit(request):
    """Редактирование профиля писателя"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к редактированию профиля писателя'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    try:
        writer_profile = request.user.writer_profile
    except WriterProfile.DoesNotExist:
        writer_profile = WriterProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = WriterProfileForm(request.POST, instance=writer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлен!'))
            return redirect('writer:dashboard')
    else:
        form = WriterProfileForm(instance=writer_profile)
    
    context = {
        'form': form,
        'writer_profile': writer_profile,
    }
    
    return render(request, 'writer/profile_edit.html', context)


@login_required
def post_create(request):
    """Создание нового блог-поста"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к созданию постов'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, user=request.user)
        if form.is_valid():
            post = form.save()
            messages.success(request, _('Пост успешно создан!'))
            return redirect('writer:post_edit', pk=post.pk)
    else:
        form = BlogPostForm(user=request.user)
    
    context = {
        'form': form,
        'action': _('Создать'),
    }
    
    return render(request, 'writer/post_form.html', context)


@login_required
def post_edit(request, pk):
    """Редактирование блог-поста"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к редактированию постов'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Пост успешно обновлен!'))
            return redirect('writer:post_edit', pk=post.pk)
    else:
        form = BlogPostForm(instance=post, user=request.user)
    
    context = {
        'form': form,
        'post': post,
        'action': _('Редактировать'),
    }
    
    return render(request, 'writer/post_form.html', context)


@login_required
def post_list(request):
    """Список постов писателя"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к списку постов'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter == 'published':
        posts = posts.filter(is_published=True)
    elif status_filter == 'draft':
        posts = posts.filter(is_published=False)
    
    # Пагинация
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'writer/post_list.html', context)


@login_required
def post_delete(request, pk):
    """Удаление блог-поста"""
    try:
        parent_profile = request.user.parent_profile
        if not parent_profile.is_writer:
            messages.error(request, _('У вас нет доступа к удалению постов'))
            return redirect('home')
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден'))
        return redirect('home')
    
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Пост успешно удален!'))
        return redirect('writer:post_list')
    
    context = {
        'post': post,
    }
    
    return render(request, 'writer/post_confirm_delete.html', context)
