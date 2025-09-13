from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BabyGrowth, BabySleep, BabyCry, BabyFeeding, BabyVaccination
from .forms import BabyGrowthForm, BabySleepForm, BabyCryForm, BabyFeedingForm, BabyVaccinationForm
from accounts.models import Child


@login_required
def tracker_dashboard(request):
    """Главная страница трекера - список детей"""
    # Получаем профиль пользователя
    try:
        profile = request.user.parent_profile
        family = profile.family if profile else None
    except:
        family = None
    
    # Получаем детей из семьи
    if family:
        children = Child.objects.filter(family=family)
    else:
        children = Child.objects.none()
    
    context = {
        'children': children,
        'family': family,
    }
    return render(request, 'tracker/dashboard.html', context)


# Growth Views
class GrowthListView(LoginRequiredMixin, ListView):
    model = BabyGrowth
    template_name = 'tracker/growth_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            profile = self.request.user.parent_profile
            family = profile.family if profile else None
        except:
            family = None
        
        if family:
            return BabyGrowth.objects.filter(family=family)
        else:
            return BabyGrowth.objects.filter(user=self.request.user)


class GrowthCreateView(LoginRequiredMixin, CreateView):
    model = BabyGrowth
    form_class = BabyGrowthForm
    template_name = 'tracker/growth_form.html'
    success_url = reverse_lazy('tracker:growth_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except:
            pass
        messages.success(self.request, _('Запись о росте и весе добавлена!'))
        return super().form_valid(form)


class GrowthUpdateView(LoginRequiredMixin, UpdateView):
    model = BabyGrowth
    form_class = BabyGrowthForm
    template_name = 'tracker/growth_form.html'
    success_url = reverse_lazy('tracker:growth_list')
    
    def get_queryset(self):
        return BabyGrowth.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Запись о росте и весе обновлена!'))
        return super().form_valid(form)


class GrowthDeleteView(LoginRequiredMixin, DeleteView):
    model = BabyGrowth
    template_name = 'tracker/growth_confirm_delete.html'
    success_url = reverse_lazy('tracker:growth_list')
    
    def get_queryset(self):
        return BabyGrowth.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Запись о росте и весе удалена!'))
        return super().delete(request, *args, **kwargs)


# Sleep Views
class SleepListView(LoginRequiredMixin, ListView):
    model = BabySleep
    template_name = 'tracker/sleep_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            profile = self.request.user.parent_profile
            family = profile.family if profile else None
        except:
            family = None
        
        if family:
            return BabySleep.objects.filter(family=family)
        else:
            return BabySleep.objects.filter(user=self.request.user)


class SleepCreateView(LoginRequiredMixin, CreateView):
    model = BabySleep
    form_class = BabySleepForm
    template_name = 'tracker/sleep_form.html'
    success_url = reverse_lazy('tracker:sleep_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except:
            pass
        messages.success(self.request, _('Запись о сне добавлена!'))
        return super().form_valid(form)


class SleepUpdateView(LoginRequiredMixin, UpdateView):
    model = BabySleep
    form_class = BabySleepForm
    template_name = 'tracker/sleep_form.html'
    success_url = reverse_lazy('tracker:sleep_list')
    
    def get_queryset(self):
        return BabySleep.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Запись о сне обновлена!'))
        return super().form_valid(form)


class SleepDeleteView(LoginRequiredMixin, DeleteView):
    model = BabySleep
    template_name = 'tracker/sleep_confirm_delete.html'
    success_url = reverse_lazy('tracker:sleep_list')
    
    def get_queryset(self):
        return BabySleep.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Запись о сне удалена!'))
        return super().delete(request, *args, **kwargs)


# Cry Views
class CryListView(LoginRequiredMixin, ListView):
    model = BabyCry
    template_name = 'tracker/cry_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            profile = self.request.user.parent_profile
            family = profile.family if profile else None
        except:
            family = None
        
        if family:
            return BabyCry.objects.filter(family=family)
        else:
            return BabyCry.objects.filter(user=self.request.user)


class CryCreateView(LoginRequiredMixin, CreateView):
    model = BabyCry
    form_class = BabyCryForm
    template_name = 'tracker/cry_form.html'
    success_url = reverse_lazy('tracker:cry_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except:
            pass
        messages.success(self.request, _('Запись о плаче добавлена!'))
        return super().form_valid(form)


class CryUpdateView(LoginRequiredMixin, UpdateView):
    model = BabyCry
    form_class = BabyCryForm
    template_name = 'tracker/cry_form.html'
    success_url = reverse_lazy('tracker:cry_list')
    
    def get_queryset(self):
        return BabyCry.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Запись о плаче обновлена!'))
        return super().form_valid(form)


class CryDeleteView(LoginRequiredMixin, DeleteView):
    model = BabyCry
    template_name = 'tracker/cry_confirm_delete.html'
    success_url = reverse_lazy('tracker:cry_list')
    
    def get_queryset(self):
        return BabyCry.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Запись о плаче удалена!'))
        return super().delete(request, *args, **kwargs)


# Feeding Views
class FeedingListView(LoginRequiredMixin, ListView):
    model = BabyFeeding
    template_name = 'tracker/feeding_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            profile = self.request.user.parent_profile
            family = profile.family if profile else None
        except:
            family = None
        
        if family:
            return BabyFeeding.objects.filter(family=family)
        else:
            return BabyFeeding.objects.filter(user=self.request.user)


class FeedingCreateView(LoginRequiredMixin, CreateView):
    model = BabyFeeding
    form_class = BabyFeedingForm
    template_name = 'tracker/feeding_form.html'
    success_url = reverse_lazy('tracker:feeding_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except:
            pass
        messages.success(self.request, _('Запись о кормлении добавлена!'))
        return super().form_valid(form)


class FeedingUpdateView(LoginRequiredMixin, UpdateView):
    model = BabyFeeding
    form_class = BabyFeedingForm
    template_name = 'tracker/feeding_form.html'
    success_url = reverse_lazy('tracker:feeding_list')
    
    def get_queryset(self):
        return BabyFeeding.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Запись о кормлении обновлена!'))
        return super().form_valid(form)


class FeedingDeleteView(LoginRequiredMixin, DeleteView):
    model = BabyFeeding
    template_name = 'tracker/feeding_confirm_delete.html'
    success_url = reverse_lazy('tracker:feeding_list')
    
    def get_queryset(self):
        return BabyFeeding.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Запись о кормлении удалена!'))
        return super().delete(request, *args, **kwargs)


# Vaccination Views
class VaccinationListView(LoginRequiredMixin, ListView):
    model = BabyVaccination
    template_name = 'tracker/vaccination_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            profile = self.request.user.parent_profile
            family = profile.family if profile else None
        except:
            family = None
        
        if family:
            return BabyVaccination.objects.filter(family=family)
        else:
            return BabyVaccination.objects.filter(user=self.request.user)


class VaccinationCreateView(LoginRequiredMixin, CreateView):
    model = BabyVaccination
    form_class = BabyVaccinationForm
    template_name = 'tracker/vaccination_form.html'
    success_url = reverse_lazy('tracker:vaccination_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            profile = self.request.user.parent_profile
            form.instance.family = profile.family if profile else None
        except:
            pass
        messages.success(self.request, _('Запись о прививке добавлена!'))
        return super().form_valid(form)


class VaccinationUpdateView(LoginRequiredMixin, UpdateView):
    model = BabyVaccination
    form_class = BabyVaccinationForm
    template_name = 'tracker/vaccination_form.html'
    success_url = reverse_lazy('tracker:vaccination_list')
    
    def get_queryset(self):
        return BabyVaccination.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Запись о прививке обновлена!'))
        return super().form_valid(form)


class VaccinationDeleteView(LoginRequiredMixin, DeleteView):
    model = BabyVaccination
    template_name = 'tracker/vaccination_confirm_delete.html'
    success_url = reverse_lazy('tracker:vaccination_list')
    
    def get_queryset(self):
        return BabyVaccination.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Запись о прививке удалена!'))
        return super().delete(request, *args, **kwargs)
