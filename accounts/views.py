from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ParentRegistrationForm, ParentProfileForm, FamilyConnectForm, ChildForm, WriterApplicationForm
from .models import ParentProfile, Family, Child, WriterApplication
from tracker.models import BabyGrowth, BabySleep, BabyCry, BabyFeeding, BabyVaccination


class ParentRegistrationView(CreateView):
    form_class = ParentRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Регистрация успешна! Теперь вы можете войти в систему.'))
        return response


@login_required
def profile_view(request):
    try:
        profile = request.user.parent_profile
        family = profile.family if profile else None
        children = Child.objects.filter(family=family) if family else Child.objects.none()
    except ParentProfile.DoesNotExist:
        profile = None
        family = None
        children = Child.objects.none()
    
    context = {
        'profile': profile,
        'family': family,
        'children': children,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Отдельная страница для редактирования профиля"""
    try:
        profile = request.user.parent_profile
    except ParentProfile.DoesNotExist:
        # Создаем профиль, если его нет
        family = Family.objects.create(name=f"Семья {request.user.username}")
        profile = ParentProfile.objects.create(
            user=request.user,
            user_type='parent',
            family=family
        )
    
    if request.method == 'POST':
        form = ParentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, _('Профиль обновлен!'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = ParentProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def family_connect_view(request):
    """Представление для подключения к семье"""
    try:
        profile = request.user.parent_profile
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден. Сначала заполните профиль.'))
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = FamilyConnectForm(request.POST)
        if form.is_valid():
            family = form.cleaned_data['family_code']
            # Проверяем, что пользователь не пытается подключиться к своей же семье
            if profile.family == family:
                messages.warning(request, _('Вы уже подключены к этой семье.'))
            else:
                # Подключаем к новой семье
                profile.family = family
                profile.save()
                messages.success(request, _('Вы успешно подключились к семье!'))
                return redirect('accounts:profile')
    else:
        form = FamilyConnectForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/family_connect.html', context)


@login_required
def family_disconnect_view(request):
    """Представление для отключения от семьи"""
    try:
        profile = request.user.parent_profile
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if profile.family:
        # Создаем новую семью для пользователя
        new_family = Family.objects.create(name=f"Семья {request.user.username}")
        profile.family = new_family
        profile.save()
        messages.success(request, _('Вы отключились от семьи и создали новую.'))
    else:
        messages.warning(request, _('Вы не подключены к семье.'))
    
    return redirect('accounts:profile')


def custom_logout_view(request):
    """Собственное представление для выхода"""
    logout(request)
    messages.success(request, _('Вы успешно вышли из системы.'))
    return render(request, 'accounts/logout.html')


@login_required
def family_management_view(request):
    """Управление семьей - главная страница"""
    try:
        profile = request.user.parent_profile
        family = profile.family
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if not family:
        messages.error(request, _('Вы не подключены к семье.'))
        return redirect('accounts:profile')
    
    # Получаем всех детей в семье
    children = Child.objects.filter(family=family).order_by('-created_at')
    
    # Получаем всех родителей в семье
    parents = ParentProfile.objects.filter(family=family)
    
    context = {
        'family': family,
        'children': children,
        'parents': parents,
        'profile': profile,
    }
    return render(request, 'accounts/family_management.html', context)


@login_required
def child_detail_view(request, child_id):
    """Детальная страница ребенка с полной статистикой"""
    try:
        profile = request.user.parent_profile
        family = profile.family if profile else None
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if not family:
        messages.error(request, _('Вы не подключены к семье.'))
        return redirect('accounts:profile')
    
    # Получаем ребенка
    child = get_object_or_404(Child, id=child_id, family=family)
    
    # Получаем статистику по ребенку
    growth_records = BabyGrowth.objects.filter(child=child).order_by('-date')[:10]
    sleep_records = BabySleep.objects.filter(child=child).order_by('-date')[:10]
    cry_records = BabyCry.objects.filter(child=child).order_by('-date')[:10]
    feeding_records = BabyFeeding.objects.filter(child=child).order_by('-date')[:10]
    vaccination_records = BabyVaccination.objects.filter(child=child).order_by('-date_given')[:10]
    
    # Статистика
    total_growth_records = BabyGrowth.objects.filter(child=child).count()
    total_sleep_records = BabySleep.objects.filter(child=child).count()
    total_cry_records = BabyCry.objects.filter(child=child).count()
    total_feeding_records = BabyFeeding.objects.filter(child=child).count()
    total_vaccination_records = BabyVaccination.objects.filter(child=child).count()
    
    # Последние записи
    last_growth = BabyGrowth.objects.filter(child=child).order_by('-date').first()
    last_sleep = BabySleep.objects.filter(child=child).order_by('-date').first()
    last_cry = BabyCry.objects.filter(child=child).order_by('-date').first()
    last_feeding = BabyFeeding.objects.filter(child=child).order_by('-date').first()
    last_vaccination = BabyVaccination.objects.filter(child=child).order_by('-date_given').first()
    
    context = {
        'child': child,
        'family': family,
        'growth_records': growth_records,
        'sleep_records': sleep_records,
        'cry_records': cry_records,
        'feeding_records': feeding_records,
        'vaccination_records': vaccination_records,
        'total_growth_records': total_growth_records,
        'total_sleep_records': total_sleep_records,
        'total_cry_records': total_cry_records,
        'total_feeding_records': total_feeding_records,
        'total_vaccination_records': total_vaccination_records,
        'last_growth': last_growth,
        'last_sleep': last_sleep,
        'last_cry': last_cry,
        'last_feeding': last_feeding,
        'last_vaccination': last_vaccination,
    }
    return render(request, 'accounts/child_detail.html', context)


@login_required
def add_child_view(request):
    """Добавление нового ребенка"""
    try:
        profile = request.user.parent_profile
        family = profile.family
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if not family:
        messages.error(request, _('Вы не подключены к семье.'))
        return redirect('accounts:family_management')
    
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.family = family
            child.save()
            messages.success(request, _('Ребёнок успешно добавлен!'))
            return redirect('accounts:family_management')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = ChildForm()
    
    context = {
        'form': form,
        'family': family,
        'profile': profile,
    }
    return render(request, 'accounts/add_child.html', context)


@login_required
def edit_child_view(request, child_id):
    """Редактирование информации о ребенке"""
    try:
        profile = request.user.parent_profile
        family = profile.family
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if not family:
        messages.error(request, _('Вы не подключены к семье.'))
        return redirect('accounts:family_management')
    
    child = get_object_or_404(Child, id=child_id, family=family)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, _('Информация о ребёнке обновлена!'))
            return redirect('accounts:family_management')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = ChildForm(instance=child)
    
    context = {
        'form': form,
        'child': child,
        'family': family,
        'profile': profile,
    }
    return render(request, 'accounts/edit_child.html', context)


@login_required
def delete_child_view(request, child_id):
    """Удаление ребенка"""
    try:
        profile = request.user.parent_profile
        family = profile.family
    except ParentProfile.DoesNotExist:
        messages.error(request, _('Профиль не найден.'))
        return redirect('accounts:profile')
    
    if not family:
        messages.error(request, _('Вы не подключены к семье.'))
        return redirect('accounts:family_management')
    
    child = get_object_or_404(Child, id=child_id, family=family)
    
    if request.method == 'POST':
        child_name = child.name
        child.delete()
        messages.success(request, _('Ребёнок {} удален из семьи.').format(child_name))
        return redirect('accounts:family_management')
    
    context = {
        'child': child,
        'family': family,
        'profile': profile,
    }
    return render(request, 'accounts/delete_child.html', context)


def writer_application_create(request):
    """Создание заявки на роль писателя"""
    if request.method == 'POST':
        form = WriterApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            
            # Отправляем уведомление суппорту
            from notifications.models import Notification
            from django.contrib.auth.models import User
            
            # Находим всех пользователей с ролью support
            support_users = User.objects.filter(groups__name='support')
            
            for support_user in support_users:
                Notification.objects.create(
                    recipient=support_user,
                    notification_type='writer_application_submitted',
                    title=_('Новая заявка писателя'),
                    message=_('Подана новая заявка на роль писателя от {}').format(application.full_name),
                    related_object_id=application.id,
                    related_object_type='writer_application',
                    extra_data={
                        'application_id': application.id,
                        'applicant_name': application.full_name,
                        'applicant_email': application.email,
                    }
                )
            
            messages.success(request, _('Заявка успешно отправлена! Мы рассмотрим её в ближайшее время.'))
            return redirect('accounts:writer_application_success', application_id=application.id)
    else:
        form = WriterApplicationForm()
    
    return render(request, 'accounts/writer_application.html', {
        'form': form,
        'title': _('Заявка на роль писателя')
    })


def writer_application_success(request, application_id):
    """Страница успешной подачи заявки"""
    application = get_object_or_404(WriterApplication, id=application_id)
    return render(request, 'accounts/writer_application_success.html', {
        'application': application,
        'title': _('Заявка отправлена')
    })
