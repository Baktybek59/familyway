from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from healthcare.models import HealthcareCategory, HealthcareFacility, Doctor, DoctorReview, FacilityReview
from consultant.models import ConsultantProfile
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Создает тестовые данные для медицинских учреждений'

    def handle(self, *args, **options):
        # Создаем категории
        categories_data = [
            {'name': 'Больницы', 'slug': 'hospitals', 'icon': 'hospital', 'color': '#dc3545', 'order': 1},
            {'name': 'Клиники', 'slug': 'clinics', 'icon': 'building', 'color': '#17a2b8', 'order': 2},
            {'name': 'Аптеки', 'slug': 'pharmacies', 'icon': 'capsule', 'color': '#28a745', 'order': 3},
            {'name': 'Стоматологии', 'slug': 'dentistry', 'icon': 'tooth', 'color': '#ffc107', 'order': 4},
            {'name': 'Лаборатории', 'slug': 'laboratories', 'icon': 'flask', 'color': '#6f42c1', 'order': 5},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = HealthcareCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Создана категория: {category.name}')

        # Создаем медицинские учреждения
        facilities_data = [
            {
                'name': 'Городская больница №1',
                'description': 'Крупнейшая многопрофильная больница города с современным оборудованием',
                'address': 'ул. Ленина, 123, Бишкек',
                'phone': '+996 312 123456',
                'email': 'info@hospital1.kg',
                'website': 'https://hospital1.kg',
                'working_hours': 'Пн-Вс: 24/7',
                'category': categories[0]
            },
            {
                'name': 'Медицинский центр "Здоровье"',
                'description': 'Современный медицинский центр с широким спектром услуг',
                'address': 'пр. Чуй, 456, Бишкек',
                'phone': '+996 312 234567',
                'email': 'info@zdorovie.kg',
                'website': 'https://zdorovie.kg',
                'working_hours': 'Пн-Пт: 8:00-20:00, Сб: 9:00-16:00',
                'category': categories[1]
            },
            {
                'name': 'Аптека "Фармация"',
                'description': 'Сеть аптек с широким ассортиментом лекарств',
                'address': 'ул. Московская, 789, Бишкек',
                'phone': '+996 312 345678',
                'email': 'info@farmacia.kg',
                'working_hours': 'Пн-Вс: 8:00-22:00',
                'category': categories[2]
            },
            {
                'name': 'Стоматология "Белоснежка"',
                'description': 'Современная стоматологическая клиника',
                'address': 'ул. Ибраимова, 321, Бишкек',
                'phone': '+996 312 456789',
                'email': 'info@belosnezhka.kg',
                'working_hours': 'Пн-Пт: 9:00-18:00, Сб: 10:00-15:00',
                'category': categories[3]
            },
            {
                'name': 'Лаборатория "Диагностика"',
                'description': 'Современная медицинская лаборатория',
                'address': 'ул. Токтогула, 654, Бишкек',
                'phone': '+996 312 567890',
                'email': 'info@diagnostika.kg',
                'working_hours': 'Пн-Пт: 7:00-19:00, Сб: 8:00-14:00',
                'category': categories[4]
            }
        ]
        
        facilities = []
        for fac_data in facilities_data:
            facility, created = HealthcareFacility.objects.get_or_create(
                name=fac_data['name'],
                defaults=fac_data
            )
            facilities.append(facility)
            if created:
                self.stdout.write(f'Создано учреждение: {facility.name}')

        # Создаем врачей
        doctors_data = [
            {
                'first_name': 'Айгуль',
                'last_name': 'Абдыкадырова',
                'middle_name': 'Токтогуловна',
                'specialization': 'Педиатр',
                'experience_years': 15,
                'education': 'КГМА, педиатрический факультет',
                'qualifications': 'Высшая категория, кандидат медицинских наук',
                'phone': '+996 555 111111',
                'email': 'aigul@hospital1.kg',
                'bio': 'Опытный педиатр с 15-летним стажем работы',
                'facility': facilities[0]
            },
            {
                'first_name': 'Марат',
                'last_name': 'Алиев',
                'middle_name': 'Султанович',
                'specialization': 'Кардиолог',
                'experience_years': 20,
                'education': 'КГМА, лечебный факультет',
                'qualifications': 'Высшая категория, доктор медицинских наук',
                'phone': '+996 555 222222',
                'email': 'marat@zdorovie.kg',
                'bio': 'Ведущий кардиолог с международным опытом',
                'facility': facilities[1]
            },
            {
                'first_name': 'Айнура',
                'last_name': 'Кыдырова',
                'middle_name': 'Асылбековна',
                'specialization': 'Стоматолог-терапевт',
                'experience_years': 10,
                'education': 'КГМА, стоматологический факультет',
                'qualifications': 'Первая категория',
                'phone': '+996 555 333333',
                'email': 'ainura@belosnezhka.kg',
                'bio': 'Специалист по лечению и профилактике стоматологических заболеваний',
                'facility': facilities[3]
            }
        ]
        
        doctors = []
        for doc_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                first_name=doc_data['first_name'],
                last_name=doc_data['last_name'],
                defaults=doc_data
            )
            doctors.append(doctor)
            if created:
                self.stdout.write(f'Создан врач: {doctor.full_name}')

        # Связываем врачей с консультантами
        try:
            # Получаем существующих консультантов
            consultants = ConsultantProfile.objects.all()
            if consultants.exists():
                # Связываем всех врачей с консультантами
                for i, doctor in enumerate(doctors):
                    if i < len(consultants):
                        doctor.consultant = consultants[i]
                        doctor.save()
                        self.stdout.write(f'Связан врач {doctor.full_name} с консультантом {consultants[i].full_name}')
                    else:
                        self.stdout.write(f'Нет консультанта для врача {doctor.full_name}')
            else:
                self.stdout.write('Консультанты не найдены. Создайте консультантов сначала.')
        except Exception as e:
            self.stdout.write(f'Ошибка при связывании врачей с консультантами: {e}')

        # Создаем пользователя для отзывов
        user, created = User.objects.get_or_create(
            username='reviewer',
            defaults={
                'email': 'reviewer@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        if created:
            user.set_password('reviewer123')
            user.save()
            self.stdout.write('Создан пользователь для отзывов')

        # Создаем отзывы о врачах
        doctor_reviews_data = [
            {
                'doctor': doctors[0],
                'user': user,
                'rating': 5,
                'title': 'Отличный врач!',
                'comment': 'Очень внимательный и профессиональный врач. Ребенок не боялся идти на прием.',
                'visit_date': date.today() - timedelta(days=5),
                'is_verified': True
            },
            {
                'doctor': doctors[1],
                'user': user,
                'rating': 4,
                'title': 'Хороший специалист',
                'comment': 'Врач провел тщательное обследование и дал подробные рекомендации.',
                'visit_date': date.today() - timedelta(days=10),
                'is_verified': True
            },
            {
                'doctor': doctors[2],
                'user': user,
                'rating': 5,
                'title': 'Рекомендую!',
                'comment': 'Безболезненное лечение, современное оборудование, приятный персонал.',
                'visit_date': date.today() - timedelta(days=3),
                'is_verified': True
            }
        ]
        
        for review_data in doctor_reviews_data:
            review, created = DoctorReview.objects.get_or_create(
                doctor=review_data['doctor'],
                user=review_data['user'],
                defaults=review_data
            )
            if created:
                self.stdout.write(f'Создан отзыв о враче: {review.doctor.full_name}')

        # Создаем отзывы об учреждениях
        facility_reviews_data = [
            {
                'facility': facilities[0],
                'user': user,
                'rating': 4,
                'title': 'Хорошая больница',
                'comment': 'Современное оборудование, квалифицированный персонал. Единственный минус - долгое ожидание.',
                'visit_date': date.today() - timedelta(days=7),
                'is_verified': True
            },
            {
                'facility': facilities[1],
                'user': user,
                'rating': 5,
                'title': 'Отличный медицинский центр',
                'comment': 'Быстрое обслуживание, вежливый персонал, современное оборудование.',
                'visit_date': date.today() - timedelta(days=12),
                'is_verified': True
            },
            {
                'facility': facilities[2],
                'user': user,
                'rating': 4,
                'title': 'Удобная аптека',
                'comment': 'Широкий ассортимент, доступные цены, удобное расположение.',
                'visit_date': date.today() - timedelta(days=2),
                'is_verified': True
            }
        ]
        
        for review_data in facility_reviews_data:
            review, created = FacilityReview.objects.get_or_create(
                facility=review_data['facility'],
                user=review_data['user'],
                defaults=review_data
            )
            if created:
                self.stdout.write(f'Создан отзыв об учреждении: {review.facility.name}')

        # Обновляем рейтинги
        for doctor in doctors:
            doctor.update_rating()
        
        for facility in facilities:
            facility.update_rating()

        self.stdout.write(
            self.style.SUCCESS('Тестовые данные для медицинских учреждений успешно созданы!')
        )
