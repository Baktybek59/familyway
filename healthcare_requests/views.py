from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import HealthcareFacilityRequest, FacilityDashboard, FacilityNotification
from .forms import HealthcareFacilityRequestForm, FacilityRequestReviewForm, FacilityLoginForm
from healthcare.models import HealthcareFacility, Doctor
from consultant.models import Consultation


def facility_request_create(request):
    """Создание заявки медицинского учреждения"""
    if request.method == 'POST':
        form = HealthcareFacilityRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save()
            
            # Создаем уведомление
            FacilityNotification.objects.create(
                facility_request=request_obj,
                notification_type='request_approved',  # Временно, будет изменено при обработке
                title=_('Заявка подана'),
                message=_('Ваша заявка на добавление в каталог успешно подана. Мы рассмотрим её в ближайшее время.')
            )
            
            messages.success(request, _('Заявка успешно подана! Мы рассмотрим её в ближайшее время.'))
            return redirect('healthcare_requests:request_success', request_id=request_obj.id)
    else:
        form = HealthcareFacilityRequestForm()
    
    return render(request, 'healthcare_requests/request_form.html', {
        'form': form,
        'title': _('Подача заявки')
    })


def facility_request_success(request, request_id):
    """Страница успешной подачи заявки"""
    request_obj = get_object_or_404(HealthcareFacilityRequest, id=request_id)
    return render(request, 'healthcare_requests/request_success.html', {
        'request_obj': request_obj
    })


def facility_login(request):
    """Вход для медицинского учреждения"""
    # Обработка выхода
    if request.method == 'POST' and request.POST.get('action') == 'logout':
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, _('Вы успешно вышли из системы'))
        return redirect('healthcare_requests:facility_login')
    
    # Если пользователь уже авторизован, перенаправляем на дашборд
    if request.user.is_authenticated:
        try:
            facility_request = HealthcareFacilityRequest.objects.get(
                username=request.user.username,
                status='approved'
            )
            return redirect('healthcare_requests:facility_dashboard')
        except HealthcareFacilityRequest.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = FacilityLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Ищем заявку с таким логином
            try:
                facility_request = HealthcareFacilityRequest.objects.get(
                    username=username,
                    status='approved'
                )
                
                # Проверяем пароль
                if facility_request.password == password:
                    # Создаем или получаем пользователя
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': facility_request.email,
                            'first_name': facility_request.contact_person,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        user.set_password(password)
                        user.save()
                    
                    # Логиним пользователя
                    user = authenticate(username=username, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, _('Добро пожаловать в дашборд учреждения!'))
                        return redirect('healthcare_requests:facility_dashboard')
                    else:
                        messages.error(request, _('Ошибка аутентификации'))
                else:
                    messages.error(request, _('Неверный пароль'))
            except HealthcareFacilityRequest.DoesNotExist:
                messages.error(request, _('Учреждение с таким логином не найдено или не одобрено'))
    else:
        form = FacilityLoginForm()
    
    return render(request, 'healthcare_requests/facility_login.html', {
        'form': form,
        'title': _('Вход для учреждения')
    })


@login_required
def facility_dashboard(request):
    """Дашборд медицинского учреждения"""
    # Проверяем, что пользователь авторизован и является медицинским учреждением
    if not request.user.is_authenticated:
        return redirect('healthcare_requests:facility_login')
    
    # Получаем заявку учреждения
    try:
        facility_request = HealthcareFacilityRequest.objects.get(
            username=request.user.username,
            status='approved'
        )
    except HealthcareFacilityRequest.DoesNotExist:
        messages.error(request, _('Учреждение не найдено или не одобрено'))
        return redirect('healthcare_requests:facility_login')
    
    # Получаем или создаем дашборд
    dashboard, created = FacilityDashboard.objects.get_or_create(
        facility_request=facility_request
    )
    
    # Обновляем статистику
    dashboard.update_statistics()
    
    # Получаем последние уведомления
    notifications = FacilityNotification.objects.filter(
        facility_request=facility_request
    ).order_by('-created_at')[:5]
    
    # Получаем последние консультации (если есть связанные объекты)
    recent_consultations = []
    try:
        recent_consultations = Consultation.objects.filter(
            doctor__facility__name=facility_request.facility_name
        ).select_related('parent', 'doctor').order_by('-created_at')[:5]
    except Exception as e:
        print(f"Ошибка при получении консультаций: {e}")
    
    # Получаем врачей учреждения (если есть связанные объекты)
    doctors = []
    try:
        doctors = Doctor.objects.filter(
            facility__name=facility_request.facility_name
        ).select_related('facility')[:10]
    except Exception as e:
        print(f"Ошибка при получении врачей: {e}")
    
    context = {
        'facility_request': facility_request,
        'dashboard': dashboard,
        'notifications': notifications,
        'recent_consultations': recent_consultations,
        'doctors': doctors,
        'title': _('Дашборд учреждения')
    }
    
    return render(request, 'healthcare_requests/facility_dashboard.html', context)


@staff_member_required
def admin_request_list(request):
    """Список заявок для администратора"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    requests = HealthcareFacilityRequest.objects.all()
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    if search_query:
        requests = requests.filter(
            Q(facility_name__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'healthcare_requests/admin_request_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'title': _('Управление заявками')
    })


@staff_member_required
def admin_request_detail(request, request_id):
    """Детальная страница заявки для администратора"""
    request_obj = get_object_or_404(HealthcareFacilityRequest, id=request_id)
    
    if request.method == 'POST':
        form = FacilityRequestReviewForm(request.POST, instance=request_obj)
        if form.is_valid():
            old_status = request_obj.status
            form.save()
            
            # Обновляем время обработки
            request_obj.processed_by = request.user
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            # Создаем уведомление для учреждения
            if old_status != request_obj.status:
                notification_type = 'request_approved' if request_obj.status == 'approved' else 'request_rejected'
                title = _('Заявка одобрена') if request_obj.status == 'approved' else _('Заявка отклонена')
                message = _('Ваша заявка была одобрена. Теперь вы можете войти в систему.') if request_obj.status == 'approved' else _('Ваша заявка была отклонена.')
                
                FacilityNotification.objects.create(
                    facility_request=request_obj,
                    notification_type=notification_type,
                    title=title,
                    message=message
                )
                
                # Отправляем email уведомление
                send_mail(
                    title,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [request_obj.email],
                    fail_silently=False,
                )
            
            messages.success(request, _('Заявка обновлена'))
            return redirect('healthcare_requests:admin_request_detail', request_id=request_id)
    else:
        form = FacilityRequestReviewForm(instance=request_obj)
    
    return render(request, 'healthcare_requests/admin_request_detail.html', {
        'request_obj': request_obj,
        'form': form,
        'title': _('Заявка учреждения')
    })


@login_required
def mark_notification_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    notification = get_object_or_404(
        FacilityNotification,
        id=notification_id,
        facility_request__username=request.user.username
    )
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'status': 'success'})


@login_required
def facility_doctors(request):
    """Управление врачами учреждения"""
    # Проверяем, что пользователь авторизован и является медицинским учреждением
    if not request.user.is_authenticated:
        return redirect('healthcare_requests:facility_login')
    
    # Получаем заявку учреждения
    try:
        facility_request = HealthcareFacilityRequest.objects.get(
            username=request.user.username,
            status='approved'
        )
    except HealthcareFacilityRequest.DoesNotExist:
        messages.error(request, _('Учреждение не найдено или не одобрено'))
        return redirect('healthcare_requests:facility_login')
    
    # Получаем врачей учреждения
    doctors = Doctor.objects.filter(
        facility__name=facility_request.facility_name
    ).select_related('facility').order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(doctors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facility_request': facility_request,
        'page_obj': page_obj,
        'title': _('Управление врачами')
    }
    
    return render(request, 'healthcare_requests/facility_doctors.html', context)


@login_required
def facility_consultations(request):
    """Консультации учреждения"""
    # Проверяем, что пользователь авторизован и является медицинским учреждением
    if not request.user.is_authenticated:
        return redirect('healthcare_requests:facility_login')
    
    # Получаем заявку учреждения
    try:
        facility_request = HealthcareFacilityRequest.objects.get(
            username=request.user.username,
            status='approved'
        )
    except HealthcareFacilityRequest.DoesNotExist:
        messages.error(request, _('Учреждение не найдено или не одобрено'))
        return redirect('healthcare_requests:facility_login')
    
    # Получаем консультации учреждения
    consultations = Consultation.objects.filter(
        doctor__facility__name=facility_request.facility_name
    ).select_related('parent', 'doctor').order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        consultations = consultations.filter(status=status_filter)
    
    # Пагинация
    paginator = Paginator(consultations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facility_request': facility_request,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'title': _('Консультации')
    }
    
    return render(request, 'healthcare_requests/facility_consultations.html', context)


@login_required
def facility_analytics(request):
    """Аналитика учреждения"""
    # Проверяем, что пользователь авторизован и является медицинским учреждением
    if not request.user.is_authenticated:
        return redirect('healthcare_requests:facility_login')
    
    # Получаем заявку учреждения
    try:
        facility_request = HealthcareFacilityRequest.objects.get(
            username=request.user.username,
            status='approved'
        )
    except HealthcareFacilityRequest.DoesNotExist:
        messages.error(request, _('Учреждение не найдено или не одобрено'))
        return redirect('healthcare_requests:facility_login')
    
    # Получаем или создаем дашборд
    dashboard, created = FacilityDashboard.objects.get_or_create(
        facility_request=facility_request
    )
    
    # Обновляем статистику
    dashboard.update_statistics()
    
    # Получаем врачей учреждения
    doctors = Doctor.objects.filter(
        facility__name=facility_request.facility_name
    ).select_related('facility')
    
    # Получаем консультации за последние 30 дней
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    recent_consultations = Consultation.objects.filter(
        doctor__facility__name=facility_request.facility_name,
        created_at__gte=thirty_days_ago
    ).select_related('parent', 'doctor')
    
    # Статистика по врачам
    doctor_stats = []
    for doctor in doctors:
        doctor_consultations = recent_consultations.filter(doctor=doctor)
        doctor_stats.append({
            'doctor': doctor,
            'consultations_count': doctor_consultations.count(),
            'average_rating': doctor.rating,
            'reviews_count': doctor.reviews.count() if hasattr(doctor, 'reviews') else 0
        })
    
    context = {
        'facility_request': facility_request,
        'dashboard': dashboard,
        'doctor_stats': doctor_stats,
        'recent_consultations': recent_consultations[:10],
        'title': _('Аналитика')
    }
    
    return render(request, 'healthcare_requests/facility_analytics.html', context)


@login_required
def facility_notifications(request):
    """Уведомления учреждения"""
    # Проверяем, что пользователь авторизован и является медицинским учреждением
    if not request.user.is_authenticated:
        return redirect('healthcare_requests:facility_login')
    
    # Получаем заявку учреждения
    try:
        facility_request = HealthcareFacilityRequest.objects.get(
            username=request.user.username,
            status='approved'
        )
    except HealthcareFacilityRequest.DoesNotExist:
        messages.error(request, _('Учреждение не найдено или не одобрено'))
        return redirect('healthcare_requests:facility_login')
    
    # Получаем уведомления учреждения
    notifications = FacilityNotification.objects.filter(
        facility_request=facility_request
    ).order_by('-created_at')
    
    # Фильтрация по типу
    type_filter = request.GET.get('type', '')
    if type_filter:
        notifications = notifications.filter(notification_type=type_filter)
    
    # Пагинация
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facility_request': facility_request,
        'page_obj': page_obj,
        'type_filter': type_filter,
        'title': _('Уведомления')
    }
    
    return render(request, 'healthcare_requests/facility_notifications.html', context)