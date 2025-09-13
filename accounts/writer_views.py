from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import WriterProfile
from .forms import WriterLoginForm, WriterProfileForm, WriterPasswordForm
from blog.models import BlogPost, BlogAnalytics


def writer_login(request):
    """Вход для писателей"""
    # Если писатель уже авторизован, перенаправляем на дашборд
    if request.user.is_authenticated and hasattr(request.user, 'accounts_writer_profile'):
        return redirect('accounts:writer_dashboard')
    
    if request.method == 'POST':
        form = WriterLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Ищем писателя с таким email
            try:
                writer = WriterProfile.objects.get(email=email, is_active=True)
                
                # Проверяем пароль
                if writer.check_password(password):
                    # Создаем или получаем пользователя
                    from django.contrib.auth.models import User
                    user, created = User.objects.get_or_create(
                        username=writer.email,
                        defaults={
                            'email': writer.email,
                            'first_name': writer.first_name,
                            'last_name': writer.last_name,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        user.set_password(password)
                        user.save()
                    
                    # Связываем пользователя с писателем
                    writer.user = user
                    writer.save()
                    
                    # Логиним пользователя
                    user = authenticate(username=writer.email, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, _('Добро пожаловать в дашборд писателя!'))
                        return redirect('accounts:writer_dashboard')
                    else:
                        messages.error(request, _('Ошибка аутентификации'))
                else:
                    messages.error(request, _('Неверный пароль'))
            except WriterProfile.DoesNotExist:
                messages.error(request, _('Писатель с таким email не найден или неактивен'))
    else:
        form = WriterLoginForm()
    
    return render(request, 'accounts/writer_login.html', {
        'form': form,
        'title': _('Вход для писателей')
    })


@login_required
def writer_dashboard(request):
    """Дашборд писателя"""
    # Проверяем, что пользователь является писателем
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    # Обновляем статистику
    writer.update_statistics()
    
    # Получаем статистику статей
    articles = BlogPost.objects.filter(author=request.user)
    published_articles = articles.filter(status='published')
    pending_articles = articles.filter(status='pending')
    draft_articles = articles.filter(status='draft')
    
    # Статистика за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_articles = articles.filter(created_at__gte=thirty_days_ago)
    recent_views = articles.filter(created_at__gte=thirty_days_ago).aggregate(
        total_views=Sum('views_count')
    )['total_views'] or 0
    
    # Топ статей по просмотрам
    top_articles = published_articles.order_by('-views_count')[:5]
    
    # Статистика по месяцам
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        month_articles = articles.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        monthly_stats.append({
            'month': month_start.strftime('%B'),
            'articles': month_articles
        })
    
    context = {
        'writer': writer,
        'articles_count': articles.count(),
        'published_count': published_articles.count(),
        'pending_count': pending_articles.count(),
        'draft_count': draft_articles.count(),
        'total_views': writer.total_views,
        'total_read_time': writer.total_read_time,
        'average_rating': writer.average_rating,
        'recent_articles_count': recent_articles.count(),
        'recent_views': recent_views,
        'top_articles': top_articles,
        'monthly_stats': monthly_stats,
        'title': _('Дашборд писателя')
    }
    
    return render(request, 'accounts/writer_dashboard.html', context)


@login_required
def writer_articles(request):
    """Статьи писателя"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    articles = BlogPost.objects.filter(author=request.user)
    
    if status:
        articles = articles.filter(status=status)
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    articles = articles.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'writer': writer,
        'page_obj': page_obj,
        'status': status,
        'sort_by': sort_by,
        'title': _('Мои статьи')
    }
    
    return render(request, 'accounts/writer_articles.html', context)


@login_required
def writer_article_create(request):
    """Создание статьи"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        language = request.POST.get('language')
        status = request.POST.get('status', 'draft')
        
        if title and content:
            article = BlogPost.objects.create(
                author=request.user,
                title=title,
                content=content,
                category=category,
                language=language,
                status=status
            )
            
            if status == 'pending':
                messages.success(request, _('Статья отправлена на одобрение'))
            else:
                messages.success(request, _('Статья сохранена как черновик'))
            
            return redirect('accounts:writer_articles')
        else:
            messages.error(request, _('Заполните все обязательные поля'))
    
    context = {
        'writer': writer,
        'title': _('Создать статью')
    }
    
    return render(request, 'accounts/writer_article_create.html', context)


@login_required
def writer_article_edit(request, article_id):
    """Редактирование статьи"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    article = get_object_or_404(BlogPost, id=article_id, author=request.user)
    
    if request.method == 'POST':
        article.title = request.POST.get('title', article.title)
        article.content = request.POST.get('content', article.content)
        article.category = request.POST.get('category', article.category)
        article.language = request.POST.get('language', article.language)
        article.status = request.POST.get('status', article.status)
        article.save()
        
        messages.success(request, _('Статья обновлена'))
        return redirect('accounts:writer_articles')
    
    context = {
        'writer': writer,
        'article': article,
        'title': _('Редактировать статью')
    }
    
    return render(request, 'accounts/writer_article_edit.html', context)


@login_required
def writer_analytics(request):
    """Аналитика писателя"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    # Получаем аналитику
    articles = BlogPost.objects.filter(author=request.user, status='published')
    
    # Статистика по статьям
    article_stats = []
    for article in articles:
        analytics = BlogAnalytics.objects.filter(blog_post=article)
        stats = {
            'article': article,
            'views': article.views_count,
            'read_time': article.read_time,
            'readers_count': analytics.count(),
            'avg_progress': analytics.aggregate(avg_progress=Avg('read_progress'))['avg_progress'] or 0,
            'avg_duration': analytics.aggregate(avg_duration=Avg('view_duration'))['avg_duration'] or 0,
        }
        article_stats.append(stats)
    
    # Статистика читателей
    all_analytics = BlogAnalytics.objects.filter(blog_post__author=request.user)
    
    # По возрасту
    age_stats = all_analytics.values('user_age').annotate(count=Count('id')).order_by('user_age')
    
    # По полу
    gender_stats = all_analytics.values('user_gender').annotate(count=Count('id'))
    
    # По городам
    city_stats = all_analytics.values('user_city').annotate(count=Count('id')).order_by('-count')[:10]
    
    # По устройствам
    device_stats = all_analytics.values('device_type').annotate(count=Count('id'))
    
    context = {
        'writer': writer,
        'article_stats': article_stats,
        'age_stats': age_stats,
        'gender_stats': gender_stats,
        'city_stats': city_stats,
        'device_stats': device_stats,
        'title': _('Аналитика')
    }
    
    return render(request, 'accounts/writer_analytics.html', context)


@login_required
def writer_profile_edit(request):
    """Редактирование профиля писателя"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    if request.method == 'POST':
        form = WriterProfileForm(request.POST, request.FILES, instance=writer)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлен'))
            return redirect('accounts:writer_dashboard')
    else:
        form = WriterProfileForm(instance=writer)
    
    context = {
        'writer': writer,
        'form': form,
        'title': _('Редактирование профиля')
    }
    
    return render(request, 'accounts/writer_profile_edit.html', context)


@login_required
def writer_password_change(request):
    """Смена пароля писателя"""
    if not hasattr(request.user, 'accounts_writer_profile'):
        messages.error(request, _('Доступ запрещен. Только для писателей.'))
        return redirect('accounts:writer_login')
    
    writer = request.user.accounts_writer_profile
    
    if request.method == 'POST':
        form = WriterPasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            
            if writer.check_password(current_password):
                writer.set_password(new_password)
                writer.save()
                messages.success(request, _('Пароль успешно изменен'))
                return redirect('accounts:writer_dashboard')
            else:
                messages.error(request, _('Неверный текущий пароль'))
    else:
        form = WriterPasswordForm()
    
    context = {
        'writer': writer,
        'form': form,
        'title': _('Смена пароля')
    }
    
    return render(request, 'accounts/writer_password_change.html', context)
