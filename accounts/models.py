from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid


class Family(models.Model):
    """Модель семьи для связи родителей"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_('Название семьи'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Семья')
        verbose_name_plural = _('Семьи')
    
    def __str__(self):
        return self.name


class Child(models.Model):
    GENDER_CHOICES = [
        ('male', _('Мальчик')),
        ('female', _('Девочка')),
    ]
    
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='children', verbose_name=_('Семья'))
    name = models.CharField(max_length=100, verbose_name=_('Имя ребёнка'))
    birth_date = models.DateField(verbose_name=_('Дата рождения'))
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name=_('Пол'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Ребёнок')
        verbose_name_plural = _('Дети')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_gender_display() if self.gender else 'Не указан'})"
    
    @property
    def age_months(self):
        from datetime import date
        today = date.today()
        return (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)
    
    @property
    def age_years(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


class ParentProfile(models.Model):
    ROLE_CHOICES = [
        ('mom', _('Мама')),
        ('dad', _('Папа')),
    ]
    
    USER_TYPE_CHOICES = [
        ('parent', _('Родитель')),
        ('writer', _('Писатель')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='parent', verbose_name=_('Тип пользователя'))
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, verbose_name=_('Роль'), null=True, blank=True)
    child_name = models.CharField(max_length=100, verbose_name=_('Имя ребёнка'), null=True, blank=True)
    child_birth_date = models.DateField(verbose_name=_('Дата рождения ребёнка'), null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name=_('Номер телефона'), null=True, blank=True)
    birth_date = models.DateField(verbose_name=_('Дата рождения'), null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name=_('Город проживания'), null=True, blank=True)
    workplace = models.CharField(max_length=200, verbose_name=_('Место работы'), null=True, blank=True)
    photo = models.ImageField(upload_to='parent_photos/', verbose_name=_('Фотография профиля'), null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='parents', verbose_name=_('Семья'), null=True, blank=True)
    family_code = models.CharField(max_length=10, unique=True, verbose_name=_('Код семьи'), null=True, blank=True)
    
    # Поля для писателей
    writing_motivation = models.TextField(verbose_name=_('Почему хотите стать писателем?'), null=True, blank=True)
    journalism_experience = models.TextField(verbose_name=_('Опыт в журналистике'), null=True, blank=True)
    years_experience = models.PositiveIntegerField(verbose_name=_('Сколько лет опыта?'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль родителя')
        verbose_name_plural = _('Профили родителей')
    
    def __str__(self):
        if self.user_type == 'writer':
            return f"Писатель - {self.user.username}"
        elif self.role and self.child_name:
            return f"{self.get_role_display()} - {self.child_name}"
        else:
            return f"Пользователь - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.family_code:
            import random
            import string
            self.family_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    @property
    def child_age_months(self):
        """Возвращает возраст ребенка в месяцах"""
        from datetime import date
        today = date.today()
        months = (today.year - self.child_birth_date.year) * 12 + today.month - self.child_birth_date.month
        return months
    
    @property
    def partner(self):
        """Возвращает партнера (второго родителя)"""
        if self.family:
            return self.family.parents.exclude(id=self.id).first()
        return None
    
    @property
    def is_writer(self):
        """Проверяет, является ли пользователь писателем"""
        return self.user_type == 'writer'
    
    @property
    def is_parent(self):
        """Проверяет, является ли пользователь родителем"""
        return self.user_type == 'parent'


class WriterProfile(models.Model):
    """Профиль писателя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_writer_profile', verbose_name=_('Пользователь'))
    first_name = models.CharField(max_length=100, verbose_name=_('Имя'))
    last_name = models.CharField(max_length=100, verbose_name=_('Фамилия'))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_('Отчество'))
    email = models.EmailField(verbose_name=_('Email'))
    password = models.CharField(max_length=128, blank=True, verbose_name=_('Пароль'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    photo = models.ImageField(upload_to='writers/', blank=True, verbose_name=_('Фото'))
    bio = models.TextField(blank=True, verbose_name=_('Биография'))
    
    # Писательская информация
    writing_motivation = models.TextField(blank=True, verbose_name=_('Почему хочет стать писателем'))
    journalism_experience = models.TextField(blank=True, verbose_name=_('Опыт в журналистике'))
    years_experience = models.PositiveIntegerField(default=0, verbose_name=_('Годы опыта'))
    specialization = models.CharField(max_length=200, blank=True, verbose_name=_('Специализация'))
    languages = models.CharField(max_length=200, blank=True, verbose_name=_('Языки'))
    
    # Статистика
    articles_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество статей'))
    total_views = models.PositiveIntegerField(default=0, verbose_name=_('Общее количество просмотров'))
    total_read_time = models.PositiveIntegerField(default=0, verbose_name=_('Общее время чтения (мин)'))
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Средний рейтинг'))
    
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Одобрен'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль писателя')
        verbose_name_plural = _('Профили писателей')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    @property
    def short_name(self):
        return f"{self.last_name} {self.first_name[0]}."
    
    def set_password(self, raw_password):
        """Установить пароль для писателя"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Проверить пароль писателя"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    def update_statistics(self):
        """Обновить статистику писателя"""
        from blog.models import BlogPost
        from blog.models import BlogLike
        
        # Подсчет статей
        self.articles_count = BlogPost.objects.filter(author=self.user).count()
        
        # Подсчет просмотров
        self.total_views = BlogPost.objects.filter(author=self.user).aggregate(
            total_views=models.Sum('views_count')
        )['total_views'] or 0
        
        # Подсчет времени чтения
        self.total_read_time = BlogPost.objects.filter(author=self.user).aggregate(
            total_read_time=models.Sum('read_time')
        )['total_read_time'] or 0
        
        # Подсчет рейтинга
        likes = BlogLike.objects.filter(post__author=self.user).count()
        if self.articles_count > 0:
            self.average_rating = likes / self.articles_count
        else:
            self.average_rating = 0
        
        self.save()


class WriterApplication(models.Model):
    """Заявка на роль писателя"""
    STATUS_CHOICES = [
        ('pending', _('На рассмотрении')),
        ('approved', _('Одобрено')),
        ('rejected', _('Отклонено')),
    ]
    
    # Личная информация
    first_name = models.CharField(max_length=100, verbose_name=_('Имя'))
    last_name = models.CharField(max_length=100, verbose_name=_('Фамилия'))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_('Отчество'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    
    # Учетные данные
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name=_('Логин'))
    password = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('Пароль'))
    
    # Писательская информация
    writing_motivation = models.TextField(verbose_name=_('Почему хотите стать писателем?'))
    journalism_experience = models.TextField(verbose_name=_('Опыт в журналистике'))
    years_experience = models.PositiveIntegerField(default=0, verbose_name=_('Годы опыта'))
    specialization = models.CharField(max_length=200, blank=True, verbose_name=_('Специализация'))
    languages = models.CharField(max_length=200, blank=True, verbose_name=_('Языки'))
    
    # Статус заявки
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Статус'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подачи'))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата рассмотрения'))
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Рассмотрел'))
    review_notes = models.TextField(blank=True, verbose_name=_('Комментарии'))
    
    class Meta:
        verbose_name = _('Заявка писателя')
        verbose_name_plural = _('Заявки писателей')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка от {self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    @property
    def short_name(self):
        return f"{self.last_name} {self.first_name[0]}."
