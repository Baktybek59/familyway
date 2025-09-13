from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from accounts.models import Family, Child


class BabyGrowth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='growth_records')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='growth_records', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='growth_records', null=True, blank=True, verbose_name=_('Ребёнок'))
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Рост (см)'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Вес (кг)'))
    date = models.DateField(verbose_name=_('Дата'))
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Запись роста и веса')
        verbose_name_plural = _('Записи роста и веса')
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.height}см, {self.weight}кг"


class BabySleep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_records')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='sleep_records', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='sleep_records', null=True, blank=True, verbose_name=_('Ребёнок'))
    date = models.DateField(verbose_name=_('Дата'))
    hours_slept = models.DecimalField(max_digits=4, decimal_places=1, verbose_name=_('Часы сна'))
    sleep_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', _('Отлично')),
            ('good', _('Хорошо')),
            ('fair', _('Удовлетворительно')),
            ('poor', _('Плохо')),
        ],
        verbose_name=_('Качество сна')
    )
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Запись сна')
        verbose_name_plural = _('Записи сна')
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.hours_slept}ч"


class BabyCry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cry_records')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='cry_records', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='cry_records', null=True, blank=True, verbose_name=_('Ребёнок'))
    date = models.DateField(verbose_name=_('Дата'))
    minutes_cried = models.IntegerField(verbose_name=_('Минуты плача'))
    reason = models.CharField(
        max_length=50,
        choices=[
            ('hunger', _('Голод')),
            ('tired', _('Усталость')),
            ('discomfort', _('Дискомфорт')),
            ('pain', _('Боль')),
            ('attention', _('Внимание')),
            ('other', _('Другое')),
        ],
        verbose_name=_('Причина плача')
    )
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Запись плача')
        verbose_name_plural = _('Записи плача')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.minutes_cried}мин"


class BabyFeeding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feeding_records')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='feeding_records', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='feeding_records', null=True, blank=True, verbose_name=_('Ребёнок'))
    date = models.DateField(verbose_name=_('Дата'))
    time = models.TimeField(verbose_name=_('Время'))
    feeding_type = models.CharField(
        max_length=20,
        choices=[
            ('breast', _('Грудное молоко')),
            ('formula', _('Смесь')),
            ('solid', _('Прикорм')),
            ('mixed', _('Смешанное')),
        ],
        verbose_name=_('Тип питания')
    )
    amount = models.CharField(max_length=50, blank=True, verbose_name=_('Количество'))
    duration = models.IntegerField(blank=True, null=True, verbose_name=_('Длительность (мин)'))
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Запись кормления')
        verbose_name_plural = _('Записи кормления')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time}: {self.get_feeding_type_display()}"


class BabyVaccination(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vaccination_records')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='vaccination_records', null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='vaccination_records', null=True, blank=True, verbose_name=_('Ребёнок'))
    vaccine_name = models.CharField(max_length=100, verbose_name=_('Название вакцины'))
    date_given = models.DateField(verbose_name=_('Дата вакцинации'))
    next_due_date = models.DateField(null=True, blank=True, verbose_name=_('Следующая вакцинация'))
    doctor_name = models.CharField(max_length=100, blank=True, verbose_name=_('Имя врача'))
    clinic_name = models.CharField(max_length=200, blank=True, verbose_name=_('Название клиники'))
    batch_number = models.CharField(max_length=50, blank=True, verbose_name=_('Номер партии'))
    reaction = models.TextField(blank=True, verbose_name=_('Реакция на вакцину'))
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Запись прививки')
        verbose_name_plural = _('Записи прививок')
        ordering = ['-date_given']
    
    def __str__(self):
        return f"{self.user.username} - {self.vaccine_name} ({self.date_given})"
