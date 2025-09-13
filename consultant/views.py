from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import ConsultantProfile, Consultation, ConsultationMessage, ConsultationReview
from .forms import (
    ConsultantProfileForm, ConsultationForm, ConsultationMessageForm, 
    ConsultationReviewForm, ConsultationSearchForm
)
from accounts.models import ParentProfile
from healthcare.models import Doctor, HealthcareFacility


class ConsultantListView(ListView):
    """Список врачей из медицинских учреждений"""
    model = Doctor
    template_name = 'consultant/consultant_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Doctor.objects.filter(
            is_active=True,
            consultant__isnull=False  # Только врачи с консультантами
        ).select_related('facility', 'consultant').order_by('-rating', 'last_name')
        
        # Фильтрация по специализации
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        # Фильтрация по опыту
        min_experience = self.request.GET.get('min_experience')
        if min_experience:
            queryset = queryset.filter(experience_years__gte=min_experience)
        
        # Фильтрация по учреждению
        facility_id = self.request.GET.get('facility')
        if facility_id:
            queryset = queryset.filter(facility_id=facility_id)
        
        # Поиск по имени или специализации
        search_query = self.request.GET.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(specialization__icontains=search_query) |
                Q(bio__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ConsultationSearchForm(self.request.GET)
        context['facilities'] = HealthcareFacility.objects.filter(is_active=True).order_by('name')
        
        # Получаем уникальные специализации из врачей
        specializations = Doctor.objects.filter(
            is_active=True,
            consultant__isnull=False
        ).values_list('specialization', flat=True).distinct().order_by('specialization')
        context['specializations'] = [(spec, spec) for spec in specializations]
        
        return context


class ConsultantDetailView(DetailView):
    """Детальная страница консультанта"""
    model = ConsultantProfile
    template_name = 'consultant/consultant_detail.html'
    context_object_name = 'consultant'
    
    def get_queryset(self):
        return ConsultantProfile.objects.filter(
            is_available=True, 
            is_verified=True
        ).select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultant = self.get_object()
        
        # Получаем отзывы о консультанте
        reviews = ConsultationReview.objects.filter(
            consultation__consultant=consultant
        ).select_related('parent').order_by('-created_at')[:5]
        
        context['recent_reviews'] = reviews
        context['average_rating'] = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        return context


@login_required
def consultant_profile_edit(request):
    """Редактирование профиля консультанта"""
    try:
        consultant_profile = request.user.consultant_profile
    except ConsultantProfile.DoesNotExist:
        messages.error(request, _('У вас нет профиля консультанта'))
        return redirect('consultant:consultant_list')
    
    if request.method == 'POST':
        form = ConsultantProfileForm(request.POST, instance=consultant_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль консультанта обновлен!'))
            return redirect('consultant:consultant_detail', pk=consultant_profile.pk)
    else:
        form = ConsultantProfileForm(instance=consultant_profile)
    
    context = {
        'form': form,
        'consultant_profile': consultant_profile,
    }
    return render(request, 'consultant/consultant_profile_edit.html', context)


class ConsultationListView(LoginRequiredMixin, ListView):
    """Список консультаций пользователя"""
    model = Consultation
    template_name = 'consultant/consultation_list.html'
    context_object_name = 'consultations'
    paginate_by = 10
    
    def get_queryset(self):
        return Consultation.objects.filter(
            parent=self.request.user
        ).select_related('doctor__facility', 'consultant__user').order_by('-created_at')


class ConsultationDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница консультации"""
    model = Consultation
    template_name = 'consultant/consultation_detail.html'
    context_object_name = 'consultation'
    
    def get_queryset(self):
        return Consultation.objects.filter(
            parent=self.request.user
        ).select_related('doctor__facility', 'consultant__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultation = self.get_object()
        
        # Получаем сообщения консультации
        messages_list = ConsultationMessage.objects.filter(
            consultation=consultation
        ).select_related('sender').order_by('created_at')
        
        context['messages'] = messages_list
        context['message_form'] = ConsultationMessageForm()
        
        # Проверяем, есть ли уже отзыв
        try:
            context['existing_review'] = consultation.review
        except ConsultationReview.DoesNotExist:
            context['existing_review'] = None
        
        return context


class ConsultationCreateView(LoginRequiredMixin, CreateView):
    """Создание новой консультации"""
    model = Consultation
    form_class = ConsultationForm
    template_name = 'consultant/consultation_form.html'
    success_url = reverse_lazy('consultant:consultation_list')
    
    def get_initial(self):
        initial = super().get_initial()
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id, is_active=True)
                initial['doctor'] = doctor
            except Doctor.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor_id = self.request.GET.get('doctor')
        if doctor_id:
            try:
                doctor = Doctor.objects.select_related('facility', 'consultant').get(
                    id=doctor_id, 
                    is_active=True
                )
                context['doctor'] = doctor
            except Doctor.DoesNotExist:
                context['doctor'] = None
        else:
            context['doctor'] = None
        return context
    
    def form_valid(self, form):
        form.instance.parent = self.request.user
        
        # Получаем семью пользователя
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except ParentProfile.DoesNotExist:
            pass
        
        messages.success(self.request, _('Консультация создана! Врач получит уведомление.'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@login_required
def send_message(request, consultation_id):
    """Отправка сообщения в консультации"""
    consultation = get_object_or_404(Consultation, id=consultation_id, parent=request.user)
    
    if request.method == 'POST':
        form = ConsultationMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.consultation = consultation
            message.sender = request.user
            message.save()
            
            # Обновляем статус консультации
            if consultation.status == 'pending':
                consultation.status = 'in_progress'
                consultation.save()
            
            messages.success(request, _('Сообщение отправлено!'))
            return redirect('consultant:consultation_detail', pk=consultation.id)
    else:
        form = ConsultationMessageForm()
    
    return render(request, 'consultant/send_message.html', {
        'form': form,
        'consultation': consultation
    })


@login_required
def add_review(request, consultation_id):
    """Добавление отзыва о консультации"""
    consultation = get_object_or_404(Consultation, id=consultation_id, parent=request.user)
    
    # Проверяем, что консультация завершена
    if consultation.status != 'completed':
        messages.error(request, _('Отзыв можно оставить только после завершения консультации'))
        return redirect('consultant:consultation_detail', pk=consultation.id)
    
    # Проверяем, что отзыва еще нет
    if hasattr(consultation, 'review'):
        messages.warning(request, _('Вы уже оставили отзыв по этой консультации'))
        return redirect('consultant:consultation_detail', pk=consultation.id)
    
    if request.method == 'POST':
        form = ConsultationReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.consultation = consultation
            review.parent = request.user
            review.save()
            
            # Обновляем рейтинг консультанта
            consultant = consultation.consultant
            avg_rating = ConsultationReview.objects.filter(
                consultation__consultant=consultant
            ).aggregate(avg_rating=Avg('rating'))['avg_rating']
            consultant.rating = avg_rating or 0
            consultant.save()
            
            messages.success(request, _('Отзыв добавлен! Спасибо за обратную связь.'))
            return redirect('consultant:consultation_detail', pk=consultation.id)
    else:
        form = ConsultationReviewForm()
    
    return render(request, 'consultant/add_review.html', {
        'form': form,
        'consultation': consultation
    })


@login_required
def mark_consultation_completed(request, consultation_id):
    """Отметить консультацию как завершенную"""
    consultation = get_object_or_404(Consultation, id=consultation_id, parent=request.user)
    
    if consultation.status == 'in_progress':
        consultation.status = 'completed'
        consultation.save()
        messages.success(request, _('Консультация отмечена как завершенная'))
    else:
        messages.warning(request, _('Консультация уже завершена или отменена'))
    
    return redirect('consultant:consultation_detail', pk=consultation.id)


@login_required
def consultant_dashboard(request):
    """Дашборд консультанта"""
    try:
        consultant_profile = request.user.consultant_profile
    except ConsultantProfile.DoesNotExist:
        messages.error(request, _('У вас нет профиля консультанта'))
        return redirect('consultant:consultant_list')
    
    # Получаем статистику
    consultations = Consultation.objects.filter(consultant=consultant_profile)
    
    stats = {
        'total_consultations': consultations.count(),
        'pending_consultations': consultations.filter(status='pending').count(),
        'in_progress_consultations': consultations.filter(status='in_progress').count(),
        'completed_consultations': consultations.filter(status='completed').count(),
        'average_rating': consultant_profile.rating,
    }
    
    # Последние консультации
    recent_consultations = consultations.order_by('-created_at')[:5]
    
    context = {
        'consultant_profile': consultant_profile,
        'stats': stats,
        'recent_consultations': recent_consultations,
    }
    
    return render(request, 'consultant/consultant_dashboard.html', context)