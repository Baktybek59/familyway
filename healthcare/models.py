from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class HealthcareCategory(models.Model):
    """Категория медицинского учреждения"""
    name = models.CharField(max_length=100, verbose_name=_('Название категории'))
    slug = models.SlugField(unique=True, verbose_name=_('URL-адрес'))
    icon = models.CharField(max_length=50, verbose_name=_('Иконка'), help_text=_('Bootstrap Icons класс'))
    color = models.CharField(max_length=20, verbose_name=_('Цвет'), help_text=_('Bootstrap цвет класс'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок сортировки'))
    
    class Meta:
        verbose_name = _('Категория медицинского учреждения')
        verbose_name_plural = _('Категории медицинских учреждений')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class HealthcareFacility(models.Model):
    """Медицинское учреждение (клиника, аптека, больница)"""
    category = models.ForeignKey(HealthcareCategory, on_delete=models.CASCADE, related_name='facilities', verbose_name=_('Категория'))
    name = models.CharField(max_length=200, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    address = models.TextField(verbose_name=_('Адрес'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    website = models.URLField(blank=True, verbose_name=_('Веб-сайт'))
    working_hours = models.TextField(blank=True, verbose_name=_('Часы работы'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Рейтинг'))
    reviews_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество отзывов'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Медицинское учреждение')
        verbose_name_plural = _('Медицинские учреждения')
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def update_rating(self):
        """Обновляет рейтинг учреждения на основе отзывов"""
        from django.db.models import Avg, Count
        stats = self.reviews.filter(is_verified=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        self.rating = stats['avg_rating'] or 0
        self.reviews_count = stats['total_reviews'] or 0
        self.save(update_fields=['rating', 'reviews_count'])


class Doctor(models.Model):
    """Врач в медицинском учреждении"""
    facility = models.ForeignKey(HealthcareFacility, on_delete=models.CASCADE, related_name='doctors', verbose_name=_('Медицинское учреждение'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', verbose_name=_('Пользователь'), null=True, blank=True)
    consultant = models.ForeignKey('consultant.ConsultantProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors', verbose_name=_('Консультант'))
    first_name = models.CharField(max_length=100, verbose_name=_('Имя'))
    last_name = models.CharField(max_length=100, verbose_name=_('Фамилия'))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_('Отчество'))
    specialization = models.CharField(max_length=200, verbose_name=_('Специализация'))
    experience_years = models.PositiveIntegerField(verbose_name=_('Опыт работы (лет)'))
    education = models.TextField(blank=True, verbose_name=_('Образование'))
    qualifications = models.TextField(blank=True, verbose_name=_('Квалификации'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    password = models.CharField(max_length=128, blank=True, verbose_name=_('Пароль'))
    photo = models.ImageField(upload_to='doctors/', blank=True, verbose_name=_('Фото'))
    bio = models.TextField(blank=True, verbose_name=_('Биография'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Рейтинг'))
    reviews_count = models.PositiveIntegerField(default=0, verbose_name=_('Количество отзывов'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    
    # Тарифы консультаций
    consultation_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Цена консультации (сом)'))
    consultation_duration = models.PositiveIntegerField(default=30, verbose_name=_('Длительность консультации (мин)'))
    is_available_for_consultation = models.BooleanField(default=True, verbose_name=_('Доступен для консультаций'))
    
    # Дополнительная информация
    working_hours = models.TextField(blank=True, verbose_name=_('Часы работы'))
    languages = models.CharField(max_length=200, blank=True, verbose_name=_('Языки'))
    awards = models.TextField(blank=True, verbose_name=_('Награды и достижения'))
    publications = models.TextField(blank=True, verbose_name=_('Публикации'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Врач')
        verbose_name_plural = _('Врачи')
        ordering = ['-rating', 'last_name', 'first_name']
    
    def __str__(self):
        return f"Др. {self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def set_password(self, raw_password):
        """Установить пароль для врача"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Проверить пароль врача"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    @property
    def short_name(self):
        return f"Др. {self.last_name} {self.first_name[0]}."
    
    def update_rating(self):
        """Обновляет рейтинг врача на основе отзывов"""
        from django.db.models import Avg, Count
        stats = self.reviews.filter(is_verified=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        self.rating = stats['avg_rating'] or 0
        self.reviews_count = stats['total_reviews'] or 0
        self.save(update_fields=['rating', 'reviews_count'])


class DoctorReview(models.Model):
    """Отзыв о враче"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Врач'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_reviews', verbose_name=_('Пользователь'))
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Оценка')
    )
    title = models.CharField(max_length=200, verbose_name=_('Заголовок отзыва'))
    comment = models.TextField(verbose_name=_('Комментарий'))
    visit_date = models.DateField(verbose_name=_('Дата посещения'))
    is_anonymous = models.BooleanField(default=False, verbose_name=_('Анонимный отзыв'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Проверен'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Отзыв о враче')
        verbose_name_plural = _('Отзывы о врачах')
        ordering = ['-created_at']
        unique_together = ['doctor', 'user']
    
    def __str__(self):
        return f"Отзыв о {self.doctor.short_name} от {self.user.username}"


class FacilityReview(models.Model):
    """Отзыв о медицинском учреждении"""
    facility = models.ForeignKey(HealthcareFacility, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Медицинское учреждение'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facility_reviews', verbose_name=_('Пользователь'))
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Оценка')
    )
    title = models.CharField(max_length=200, verbose_name=_('Заголовок отзыва'))
    comment = models.TextField(verbose_name=_('Комментарий'))
    visit_date = models.DateField(verbose_name=_('Дата посещения'))
    is_anonymous = models.BooleanField(default=False, verbose_name=_('Анонимный отзыв'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Проверен'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Отзыв о медицинском учреждении')
        verbose_name_plural = _('Отзывы о медицинских учреждениях')
        ordering = ['-created_at']
        unique_together = ['facility', 'user']
    
    def __str__(self):
        return f"Отзыв о {self.facility.name} от {self.user.username}"