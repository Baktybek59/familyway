from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .models import SupportTicket, TicketComment, SupportProfile, SupportNotification, SupportDashboard
from .forms import (
    SupportTicketForm, TicketCommentForm, TicketAssignmentForm, 
    SupportDashboardForm, DisputeTicketForm, FacilityRequestReviewForm,
    BlogApprovalForm, ForumModerationForm, SupportProfileEditForm, ReviewDeletionForm
)
from healthcare_requests.models import HealthcareFacilityRequest
from forum.models import Post
from blog.models import BlogPost
from healthcare.models import DoctorReview, FacilityReview
from accounts.models import WriterApplication, WriterProfile


def is_support_staff(user):
    """Проверяет, является ли пользователь сотрудником техподдержки"""
    return hasattr(user, 'supportprofile') and user.supportprofile.is_active


class SupportDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Дашборд техподдержки"""
    model = SupportTicket
    template_name = 'support/dashboard.html'
    context_object_name = 'tickets'
    paginate_by = 20

    def test_func(self):
        return is_support_staff(self.request.user)

    def get_queryset(self):
        queryset = SupportTicket.objects.all()
        
        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по приоритету
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Фильтрация по назначенному сотруднику
        assigned = self.request.GET.get('assigned')
        if assigned == 'me':
            queryset = queryset.filter(assigned_to__user=self.request.user)
        elif assigned == 'unassigned':
            queryset = queryset.filter(assigned_to__isnull=True)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        context['stats'] = {
            'total_tickets': SupportTicket.objects.count(),
            'open_tickets': SupportTicket.objects.filter(status='open').count(),
            'in_progress_tickets': SupportTicket.objects.filter(status='in_progress').count(),
            'resolved_tickets': SupportTicket.objects.filter(status='resolved').count(),
            'high_priority_tickets': SupportTicket.objects.filter(priority='high').count(),
            'urgent_tickets': SupportTicket.objects.filter(priority='urgent').count(),
            'approved_writers_count': WriterProfile.objects.filter(is_approved=True, is_active=True).count(),
            'approved_facilities_count': HealthcareFacilityRequest.objects.filter(status='approved').count(),
        }
        
        # Заявки учреждений
        context['facility_requests'] = HealthcareFacilityRequest.objects.filter(
            status='pending'
        ).order_by('-created_at')[:5]
        
        # Заявки писателей
        context['writer_applications'] = WriterApplication.objects.filter(
            status='pending'
        ).order_by('-created_at')[:5]
        
        # Одобренные писатели
        context['approved_writers'] = WriterProfile.objects.filter(
            is_approved=True,
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Одобренные учреждения
        context['approved_facilities'] = HealthcareFacilityRequest.objects.filter(
            status='approved'
        ).order_by('-created_at')[:5]
        
        # Последние тикеты
        context['recent_tickets'] = SupportTicket.objects.order_by('-created_at')[:10]
        
        # Уведомления
        context['notifications'] = SupportNotification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        # Категории для фильтрации
        context['categories'] = SupportTicket.CATEGORY_CHOICES
        context['priorities'] = SupportTicket.PRIORITY_CHOICES
        context['statuses'] = SupportTicket.STATUS_CHOICES
        
        return context


class TicketDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Детальный просмотр тикета"""
    model = SupportTicket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'

    def test_func(self):
        return is_support_staff(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TicketCommentForm()
        context['assignment_form'] = TicketAssignmentForm(instance=self.object)
        context['comments'] = self.object.comments.all()
        return context


class TicketCreateView(LoginRequiredMixin, CreateView):
    """Создание тикета"""
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = 'support/ticket_create.html'
    success_url = reverse_lazy('support:dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class DisputeTicketCreateView(LoginRequiredMixin, CreateView):
    """Создание тикета для спора врач-родитель"""
    model = SupportTicket
    form_class = DisputeTicketForm
    template_name = 'support/dispute_ticket_create.html'
    success_url = reverse_lazy('support:dashboard')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.category = 'dispute'
        return super().form_valid(form)


@login_required
@user_passes_test(is_support_staff)
def add_comment(request, ticket_id):
    """Добавление комментария к тикету"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, _('Комментарий добавлен'))
        else:
            messages.error(request, _('Ошибка при добавлении комментария'))
    
    return redirect('support:ticket_detail', pk=ticket_id)


@login_required
@user_passes_test(is_support_staff)
def assign_ticket(request, ticket_id):
    """Назначение тикета сотруднику"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketAssignmentForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, _('Тикет назначен'))
        else:
            messages.error(request, _('Ошибка при назначении тикета'))
    
    return redirect('support:ticket_detail', pk=ticket_id)


@login_required
@user_passes_test(is_support_staff)
def facility_requests(request):
    """Список заявок учреждений"""
    requests = HealthcareFacilityRequest.objects.filter(status='pending').order_by('-created_at')
    
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/facility_requests.html', {
        'page_obj': page_obj,
        'requests': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def facility_request_detail(request, request_id):
    """Детальный просмотр заявки учреждения"""
    facility_request = get_object_or_404(HealthcareFacilityRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            facility_request.status = 'approved'
            facility_request.save()
            messages.success(request, _('Заявка одобрена'))
        elif action == 'reject':
            facility_request.status = 'rejected'
            facility_request.save()
            messages.success(request, _('Заявка отклонена'))
    
    return render(request, 'support/facility_request_detail.html', {
        'facility_request': facility_request,
    })


@login_required
@user_passes_test(is_support_staff)
def forum_moderation(request):
    """Модерация форума"""
    # Показываем все посты, так как в модели нет поля is_approved
    posts = Post.objects.all().order_by('-created_at')
    
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/forum_moderation.html', {
        'page_obj': page_obj,
        'posts': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def approve_forum_post(request, post_id):
    """Одобрение поста форума"""
    post = get_object_or_404(Post, id=post_id)
    # В данной модели нет поля is_approved, поэтому просто отмечаем как решение
    post.is_solution = True
    post.save()
    messages.success(request, _('Пост отмечен как решение'))
    return redirect('support:forum_moderation')


@login_required
@user_passes_test(is_support_staff)
def delete_forum_post(request, post_id):
    """Удаление поста форума"""
    post = get_object_or_404(Post, id=post_id)
    topic = post.topic
    post.delete()
    messages.success(request, _('Пост удален'))
    return redirect('support:forum_moderation')


@login_required
@user_passes_test(is_support_staff)
def edit_forum_post(request, post_id):
    """Редактирование поста форума"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            post.content = content
            post.save()
            messages.success(request, _('Пост обновлен'))
            return redirect('support:forum_moderation')
    
    return render(request, 'support/edit_forum_post.html', {
        'post': post,
    })


@login_required
@user_passes_test(is_support_staff)
def delete_forum_topic(request, topic_id):
    """Удаление темы форума"""
    from forum.models import Topic
    topic = get_object_or_404(Topic, id=topic_id)
    topic.delete()
    messages.success(request, _('Тема удалена'))
    return redirect('support:forum_moderation')


@login_required
@user_passes_test(is_support_staff)
def edit_forum_topic(request, topic_id):
    """Редактирование темы форума"""
    from forum.models import Topic
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            topic.title = title
            topic.content = content
            topic.save()
            messages.success(request, _('Тема обновлена'))
            return redirect('support:forum_moderation')
    
    return render(request, 'support/edit_forum_topic.html', {
        'topic': topic,
    })


@login_required
@user_passes_test(is_support_staff)
def blog_approval(request):
    """Одобрение статей блога"""
    posts = BlogPost.objects.filter(is_published=False).order_by('-created_at')
    
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/blog_approval.html', {
        'page_obj': page_obj,
        'posts': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def approve_blog_post(request, post_id):
    """Одобрение статьи блога"""
    post = get_object_or_404(BlogPost, id=post_id)
    post.is_published = True
    post.save()
    messages.success(request, _('Статья одобрена'))
    return redirect('support:blog_approval')


@login_required
@user_passes_test(is_support_staff)
def edit_blog_post(request, post_id):
    """Редактирование статьи блога"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        form = BlogApprovalForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, _('Статья обновлена'))
            return redirect('support:blog_approval')
    else:
        form = BlogApprovalForm(instance=post)
    
    return render(request, 'support/edit_blog_post.html', {
        'form': form,
        'post': post,
    })


@login_required
@user_passes_test(is_support_staff)
def delete_blog_post(request, post_id):
    """Удаление статьи блога"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _('Статья удалена'))
        return redirect('support:blog_approval')
    
    return render(request, 'support/delete_blog_post.html', {
        'post': post,
    })


@login_required
@user_passes_test(is_support_staff)
def blog_creators(request):
    """Управление авторами блога"""
    # Здесь можно добавить логику для управления авторами блога
    return render(request, 'support/blog_creators.html')


# @login_required
# @user_passes_test(is_support_staff)
# def review_moderation(request):
#     """Модерация отзывов"""
#     reviews = Review.objects.filter(is_approved=False).order_by('-created_at')
#     
#     paginator = Paginator(reviews, 20)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     
#     return render(request, 'support/review_moderation.html', {
#         'page_obj': page_obj,
#         'reviews': page_obj,
#     })


# @login_required
# @user_passes_test(is_support_staff)
# def approve_review(request, review_id):
#     """Одобрение отзыва"""
#     review = get_object_or_404(Review, id=review_id)
#     review.is_approved = True
#     review.save()
#     messages.success(request, _('Отзыв одобрен'))
#     return redirect('support:review_moderation')


@login_required
@user_passes_test(is_support_staff)
def mark_notification_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    notification = get_object_or_404(SupportNotification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


@login_required
@user_passes_test(is_support_staff)
def dashboard_settings(request):
    """Настройки дашборда"""
    dashboard, created = SupportDashboard.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = SupportDashboardForm(request.POST, instance=dashboard)
        if form.is_valid():
            form.save()
            messages.success(request, _('Настройки сохранены'))
            return redirect('support:dashboard')
    else:
        form = SupportDashboardForm(instance=dashboard)
    
    return render(request, 'support/dashboard_settings.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_support_staff)
def support_profile(request):
    """Профиль сотрудника техподдержки"""
    try:
        profile = request.user.supportprofile
    except SupportProfile.DoesNotExist:
        # Создаем профиль если его нет
        profile = SupportProfile.objects.create(
            user=request.user,
            employee_id=f'SUP{request.user.id:03d}',
            department='Техподдержка',
            phone=''
        )
    
    return render(request, 'support/profile.html', {
        'profile': profile,
    })


@login_required
@user_passes_test(is_support_staff)
def support_profile_edit(request):
    """Редактирование профиля сотрудника техподдержки"""
    try:
        profile = request.user.supportprofile
    except SupportProfile.DoesNotExist:
        # Создаем профиль если его нет
        profile = SupportProfile.objects.create(
            user=request.user,
            employee_id=f'SUP{request.user.id:03d}',
            department='Техподдержка',
            phone=''
        )
    
    if request.method == 'POST':
        form = SupportProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль обновлен'))
            return redirect('support:profile')
    else:
        form = SupportProfileEditForm(instance=profile)
    
    return render(request, 'support/profile_edit.html', {
        'form': form,
        'profile': profile,
    })


@login_required
@user_passes_test(is_support_staff)
def review_moderation(request):
    """Модерация отзывов"""
    # Получаем все отзывы (о врачах и учреждениях)
    doctor_reviews = DoctorReview.objects.all()
    facility_reviews = FacilityReview.objects.all()
    
    # Объединяем отзывы в один список с типом
    all_reviews = []
    for review in doctor_reviews:
        review.review_type = 'doctor'
        review.target_name = f"{review.doctor.last_name} {review.doctor.first_name} {review.doctor.middle_name}".strip()
        review.target_category = 'Врач'
        all_reviews.append(review)
    
    for review in facility_reviews:
        review.review_type = 'facility'
        review.target_name = review.facility.name
        review.target_category = review.facility.category.name
        all_reviews.append(review)
    
    # Сортируем по дате создания
    all_reviews.sort(key=lambda x: x.created_at, reverse=True)
    
    # Пагинация
    paginator = Paginator(all_reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/review_moderation.html', {
        'page_obj': page_obj,
        'reviews': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def delete_review(request, review_id):
    """Удаление отзыва с указанием причины"""
    from notifications.services import NotificationService
    
    review_type = request.GET.get('type', 'facility')
    
    if review_type == 'doctor':
        review = get_object_or_404(DoctorReview, id=review_id)
        target_name = f"{review.doctor.last_name} {review.doctor.first_name} {review.doctor.middle_name}".strip()
    else:
        review = get_object_or_404(FacilityReview, id=review_id)
        target_name = review.facility.name
    
    if request.method == 'POST':
        form = ReviewDeletionForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            
            # Создаем уведомление через основную систему
            NotificationService.create_notification(
                recipient=review.user,
                notification_type='review_deleted',
                title='Отзыв удален',
                message=f'Ваш отзыв о "{target_name}" был удален модератором.\n\nПричина: {reason}',
                sender=request.user,
                priority='high',
                related_object_id=review.id,
                related_object_type='review',
                extra_data={
                    'review_type': review_type,
                    'target_name': target_name,
                    'reason': reason,
                    'deleted_by': request.user.get_full_name()
                }
            )
            
            # Удаляем отзыв
            review.delete()
            
            messages.success(request, _('Отзыв удален. Пользователю отправлено уведомление с причиной.'))
            return redirect('support:review_moderation')
    else:
        form = ReviewDeletionForm()
    
    return render(request, 'support/delete_review.html', {
        'form': form,
        'review': review,
        'target_name': target_name,
        'review_type': review_type,
    })


@login_required
@user_passes_test(is_support_staff)
def edit_review(request, review_id):
    """Редактирование отзыва"""
    review_type = request.GET.get('type', 'facility')
    
    if review_type == 'doctor':
        review = get_object_or_404(DoctorReview, id=review_id)
        review.review_type = 'doctor'
        review.target_name = f"{review.doctor.last_name} {review.doctor.first_name} {review.doctor.middle_name}".strip()
        review.target_category = 'Врач'
    else:
        review = get_object_or_404(FacilityReview, id=review_id)
        review.review_type = 'facility'
        review.target_name = review.facility.name
        review.target_category = review.facility.category.name
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating:
            review.rating = int(rating)
            review.comment = comment
            review.save()
            messages.success(request, _('Отзыв обновлен'))
            return redirect('support:review_moderation')
    
    return render(request, 'support/edit_review.html', {
        'review': review,
    })


@login_required
@user_passes_test(is_support_staff)
def approve_review(request, review_id):
    """Одобрение отзыва"""
    review_type = request.GET.get('type', 'facility')
    
    if review_type == 'doctor':
        review = get_object_or_404(DoctorReview, id=review_id)
    else:
        review = get_object_or_404(FacilityReview, id=review_id)
    
    review.is_approved = True
    review.save()
    messages.success(request, _('Отзыв одобрен'))
    return redirect('support:review_moderation')


@login_required
def review_deletion_notifications(request):
    """Просмотр уведомлений об удалении отзывов"""
    from notifications.models import Notification
    
    # Получаем уведомления об удалении отзывов
    notifications = Notification.objects.filter(
        recipient=request.user,
        notification_type='review_deleted'
    ).order_by('-created_at')
    
    # Отмечаем уведомления как прочитанные
    notifications.update(is_read=True)
    
    return render(request, 'support/review_deletion_notifications.html', {
        'notifications': notifications,
    })


@login_required
@user_passes_test(is_support_staff)
def writer_applications(request):
    """Список заявок писателей"""
    applications = WriterApplication.objects.filter(status='pending').order_by('-created_at')
    
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/writer_applications.html', {
        'page_obj': page_obj,
        'applications': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def writer_application_detail(request, application_id):
    """Детальный просмотр заявки писателя"""
    application = get_object_or_404(WriterApplication, id=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '')
        
        if action == 'approve':
            application.status = 'approved'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.review_notes = review_notes
            application.save()
            
            # Создаем пользователя для писателя
            from django.contrib.auth.models import User
            
            # Используем логин и пароль из заявки
            username = application.username
            
            # Создаем пользователя с паролем из заявки
            user = User.objects.create_user(
                username=username,
                email=application.email,
                first_name=application.first_name,
                last_name=application.last_name,
                password=application.password  # Используем пароль из заявки
            )
            
            # Создаем профиль писателя
            writer_profile = WriterProfile.objects.create(
                user=user,
                first_name=application.first_name,
                last_name=application.last_name,
                middle_name=application.middle_name,
                email=application.email,
                phone=application.phone,
                writing_motivation=application.writing_motivation,
                journalism_experience=application.journalism_experience,
                years_experience=application.years_experience,
                specialization=application.specialization,
                languages=application.languages,
                is_approved=True,
                is_active=True
            )
            
            # Отправляем уведомление пользователю (если есть система уведомлений)
            try:
                from notifications.services import NotificationService
                NotificationService.create_notification(
                    recipient=user,
                    notification_type='writer_application_approved',
                    title='Заявка писателя одобрена',
                    message=f'Ваша заявка на роль писателя была одобрена! Вы можете войти в систему, используя указанные при подаче заявки логин и пароль.',
                    sender=request.user,
                    priority='high',
                    related_object_id=writer_profile.id,
                    related_object_type='writer_profile',
                    extra_data={
                        'username': username,
                        'temp_password': 'temp_password_123',
                        'application_id': application.id
                    }
                )
            except ImportError:
                # Если система уведомлений недоступна, просто пропускаем
                pass
            
            messages.success(request, _('Заявка одобрена. Профиль писателя создан. Пользователь может войти с логином: {}').format(username))
            
        elif action == 'reject':
            application.status = 'rejected'
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.review_notes = review_notes
            application.save()
            
            # Отправляем уведомление пользователю (если есть система уведомлений)
            try:
                from notifications.services import NotificationService
                # Создаем временного пользователя для уведомления
                temp_user = User.objects.create_user(
                    username=f'temp_{application.id}',
                    email=application.email,
                    first_name=application.first_name,
                    last_name=application.last_name,
                    is_active=False  # Неактивный пользователь
                )
                
                NotificationService.create_notification(
                    recipient=temp_user,
                    notification_type='writer_application_rejected',
                    title='Заявка писателя отклонена',
                    message=f'К сожалению, ваша заявка на роль писателя была отклонена. Причина: {review_notes or "Не указана"}.',
                    sender=request.user,
                    priority='medium',
                    related_object_id=application.id,
                    related_object_type='writer_application',
                    extra_data={
                        'application_id': application.id,
                        'reason': review_notes
                    }
                )
            except ImportError:
                # Если система уведомлений недоступна, просто пропускаем
                pass
            
            messages.success(request, _('Заявка отклонена.'))
        
        return redirect('support:writer_applications')
    
    return render(request, 'support/writer_application_detail.html', {
        'application': application,
    })


@login_required
@user_passes_test(is_support_staff)
def writer_applications_approved(request):
    """Список одобренных заявок писателей"""
    applications = WriterApplication.objects.filter(status='approved').order_by('-reviewed_at')
    
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/writer_applications_approved.html', {
        'page_obj': page_obj,
        'applications': page_obj,
    })


@login_required
@user_passes_test(is_support_staff)
def writer_applications_rejected(request):
    """Список отклоненных заявок писателей"""
    applications = WriterApplication.objects.filter(status='rejected').order_by('-reviewed_at')
    
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'support/writer_applications_rejected.html', {
        'page_obj': page_obj,
        'applications': page_obj,
    })