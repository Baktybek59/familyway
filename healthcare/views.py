from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from .models import HealthcareCategory, HealthcareFacility, Doctor, DoctorReview, FacilityReview
from .forms import HealthcareFacilityForm, DoctorForm, DoctorReviewForm, FacilityReviewForm, DoctorLoginForm, DoctorProfileForm, DoctorPasswordForm


class HealthcareIndexView(ListView):
    """Главная страница медицинских учреждений"""
    model = HealthcareFacility
    template_name = 'healthcare/index.html'
    context_object_name = 'facilities'
    paginate_by = 12
    
    def get_queryset(self):
        return HealthcareFacility.objects.filter(is_active=True).select_related('category').prefetch_related('reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = HealthcareCategory.objects.all().order_by('order', 'name')
        return context


class HealthcareCategoryView(ListView):
    """Список учреждений по категории"""
    model = HealthcareFacility
    template_name = 'healthcare/category.html'
    context_object_name = 'facilities'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(HealthcareCategory, slug=self.kwargs['slug'])
        return HealthcareFacility.objects.filter(
            category=self.category, 
            is_active=True
        ).select_related('category').prefetch_related('reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = HealthcareCategory.objects.all().order_by('order', 'name')
        return context


class HealthcareFacilityDetailView(DetailView):
    """Детальная страница медицинского учреждения"""
    model = HealthcareFacility
    template_name = 'healthcare/facility_detail.html'
    context_object_name = 'facility'
    
    def get_queryset(self):
        return HealthcareFacility.objects.filter(is_active=True).select_related('category').prefetch_related('doctors', 'reviews')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facility = self.get_object()
        
        # Получаем врачей учреждения
        context['doctors'] = facility.doctors.filter(is_active=True).order_by('-rating', 'last_name')
        
        # Получаем отзывы учреждения
        context['reviews'] = facility.reviews.filter(is_verified=True).order_by('-created_at')[:10]
        
        # Статистика отзывов
        reviews_stats = facility.reviews.filter(is_verified=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        context['avg_rating'] = reviews_stats['avg_rating'] or 0
        context['total_reviews'] = reviews_stats['total_reviews'] or 0
        
        return context


class DoctorDetailView(DetailView):
    """Детальная страница врача"""
    model = Doctor
    template_name = 'healthcare/doctor_detail.html'
    context_object_name = 'doctor'
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).select_related('facility')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        
        # Получаем отзывы врача
        context['reviews'] = doctor.reviews.filter(is_verified=True).order_by('-created_at')[:10]
        
        # Статистика отзывов
        reviews_stats = doctor.reviews.filter(is_verified=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        context['avg_rating'] = reviews_stats['avg_rating'] or 0
        context['total_reviews'] = reviews_stats['total_reviews'] or 0
        
        return context


@login_required
def add_doctor_review(request, doctor_id):
    """Добавление отзыва о враче"""
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    
    if request.method == 'POST':
        form = DoctorReviewForm(request.POST)
        if form.is_valid():
            # Проверяем, не оставлял ли пользователь уже отзыв
            if DoctorReview.objects.filter(doctor=doctor, user=request.user).exists():
                messages.error(request, _('Вы уже оставляли отзыв об этом враче.'))
                return redirect('healthcare:doctor_detail', pk=doctor.id)
            
            review = form.save(commit=False)
            review.doctor = doctor
            review.user = request.user
            review.save()
            
            # Обновляем рейтинг врача
            doctor.update_rating()
            
            messages.success(request, _('Отзыв успешно добавлен!'))
            return redirect('healthcare:doctor_detail', pk=doctor.id)
    else:
        form = DoctorReviewForm()
    
    context = {
        'doctor': doctor,
        'form': form,
    }
    return render(request, 'healthcare/add_doctor_review.html', context)


@login_required
def add_facility_review(request, facility_id):
    """Добавление отзыва о медицинском учреждении"""
    facility = get_object_or_404(HealthcareFacility, id=facility_id, is_active=True)
    
    if request.method == 'POST':
        form = FacilityReviewForm(request.POST)
        if form.is_valid():
            # Проверяем, не оставлял ли пользователь уже отзыв
            if FacilityReview.objects.filter(facility=facility, user=request.user).exists():
                messages.error(request, _('Вы уже оставляли отзыв об этом учреждении.'))
                return redirect('healthcare:facility_detail', pk=facility.id)
            
            review = form.save(commit=False)
            review.facility = facility
            review.user = request.user
            review.save()
            
            # Обновляем рейтинг учреждения
            facility.update_rating()
            
            messages.success(request, _('Отзыв успешно добавлен!'))
            return redirect('healthcare:facility_detail', pk=facility.id)
    else:
        form = FacilityReviewForm()
    
    context = {
        'facility': facility,
        'form': form,
    }
    return render(request, 'healthcare/add_facility_review.html', context)


class DoctorListView(ListView):
    """Список всех врачей"""
    model = Doctor
    template_name = 'healthcare/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 20
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).select_related('facility').order_by('-rating', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facilities'] = HealthcareFacility.objects.filter(is_active=True).order_by('name')
        return context


# Admin views for creating facilities and doctors
class HealthcareFacilityCreateView(LoginRequiredMixin, CreateView):
    model = HealthcareFacility
    form_class = HealthcareFacilityForm
    template_name = 'healthcare/facility_form.html'
    success_url = reverse_lazy('healthcare:index')
    
    def form_valid(self, form):
        messages.success(self.request, _('Медицинское учреждение успешно добавлено!'))
        return super().form_valid(form)


class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'healthcare/doctor_form.html'
    success_url = reverse_lazy('healthcare:doctor_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Врач успешно добавлен!'))
        return super().form_valid(form)


def doctor_login(request):
    """Вход для врачей"""
    # Если врач уже авторизован, перенаправляем на дашборд
    if request.user.is_authenticated and hasattr(request.user, 'doctor_profile'):
        return redirect('healthcare:doctor_dashboard')
    
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Ищем врача с таким email
            try:
                doctor = Doctor.objects.get(email=email, is_active=True)
                
                # Проверяем пароль
                if doctor.check_password(password):
                    # Создаем или получаем пользователя
                    from django.contrib.auth.models import User
                    user, created = User.objects.get_or_create(
                        username=doctor.email,
                        defaults={
                            'email': doctor.email,
                            'first_name': doctor.first_name,
                            'last_name': doctor.last_name,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        user.set_password(password)
                        user.save()
                    
                    # Связываем пользователя с врачом
                    doctor.user = user
                    doctor.save()
                    
                    # Логиним пользователя
                    user = authenticate(username=doctor.email, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, _('Добро пожаловать в дашборд врача!'))
                        return redirect('healthcare:doctor_dashboard')
                    else:
                        messages.error(request, _('Ошибка аутентификации'))
                else:
                    messages.error(request, _('Неверный пароль'))
            except Doctor.DoesNotExist:
                messages.error(request, _('Врач с таким email не найден или неактивен'))
    else:
        form = DoctorLoginForm()
    
    return render(request, 'healthcare/doctor_login.html', {
        'form': form,
        'title': _('Вход для врачей')
    })


@login_required
def doctor_dashboard(request):
    """Дашборд врача"""
    # Проверяем, что пользователь является врачом
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, _('Доступ запрещен. Только для врачей.'))
        return redirect('healthcare:doctor_login')
    
    doctor = request.user.doctor_profile
    
    # Получаем статистику врача
    from consultant.models import Consultation
    consultations = Consultation.objects.filter(doctor=doctor)
    reviews = DoctorReview.objects.filter(doctor=doctor)
    
    # Статистика за последние 30 дней
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_consultations = consultations.filter(created_at__gte=thirty_days_ago)
    recent_reviews = reviews.filter(created_at__gte=thirty_days_ago)
    
    # Статистика по месяцам
    monthly_stats = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        month_consultations = consultations.filter(created_at__gte=month_start, created_at__lt=month_end).count()
        monthly_stats.append({
            'month': month_start.strftime('%B'),
            'consultations': month_consultations
        })
    
    context = {
        'doctor': doctor,
        'consultations_count': consultations.count(),
        'reviews_count': reviews.count(),
        'average_rating': reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
        'recent_consultations_count': recent_consultations.count(),
        'recent_reviews_count': recent_reviews.count(),
        'monthly_stats': monthly_stats,
        'title': _('Дашборд врача')
    }
    
    return render(request, 'healthcare/doctor_dashboard.html', context)


@login_required
def doctor_consultations(request):
    """Консультации врача"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, _('Доступ запрещен. Только для врачей.'))
        return redirect('healthcare:doctor_login')
    
    doctor = request.user.doctor_profile
    from consultant.models import Consultation
    
    consultations = Consultation.objects.filter(doctor=doctor).order_by('-created_at')
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        consultations = consultations.filter(status=status)
    
    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(consultations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'doctor': doctor,
        'page_obj': page_obj,
        'status': status,
        'title': _('Мои консультации')
    }
    
    return render(request, 'healthcare/doctor_consultations.html', context)


@login_required
def doctor_consultation_detail(request, consultation_id):
    """Детали консультации"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, _('Доступ запрещен. Только для врачей.'))
        return redirect('healthcare:doctor_login')
    
    doctor = request.user.doctor_profile
    from consultant.models import Consultation
    
    consultation = get_object_or_404(Consultation, id=consultation_id, doctor=doctor)
    
    if request.method == 'POST':
        response_text = request.POST.get('response')
        if response_text:
            consultation.response = response_text
            consultation.status = 'completed'
            consultation.save()
            messages.success(request, _('Ответ отправлен пациенту'))
            return redirect('healthcare:doctor_consultation_detail', consultation_id=consultation_id)
    
    context = {
        'doctor': doctor,
        'consultation': consultation,
        'title': _('Консультация')
    }
    
    return render(request, 'healthcare/doctor_consultation_detail.html', context)


@login_required
def doctor_profile_edit(request):
    """Редактирование профиля врача"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, _('Доступ запрещен. Только для врачей.'))
        return redirect('healthcare:doctor_login')
    
    doctor = request.user.doctor_profile
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлен'))
            return redirect('healthcare:doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    context = {
        'doctor': doctor,
        'form': form,
        'title': _('Редактирование профиля')
    }
    
    return render(request, 'healthcare/doctor_profile_edit.html', context)


@login_required
def doctor_password_change(request):
    """Смена пароля врача"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, _('Доступ запрещен. Только для врачей.'))
        return redirect('healthcare:doctor_login')
    
    doctor = request.user.doctor_profile
    
    if request.method == 'POST':
        form = DoctorPasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            
            if doctor.check_password(current_password):
                doctor.set_password(new_password)
                doctor.save()
                messages.success(request, _('Пароль успешно изменен'))
                return redirect('healthcare:doctor_dashboard')
            else:
                messages.error(request, _('Неверный текущий пароль'))
    else:
        form = DoctorPasswordForm()
    
    context = {
        'doctor': doctor,
        'form': form,
        'title': _('Смена пароля')
    }
    
    return render(request, 'healthcare/doctor_password_change.html', context)