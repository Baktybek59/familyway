from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from consultant.models import ConsultantProfile


class Command(BaseCommand):
    help = 'Создает примеры консультантов-врачей'

    def handle(self, *args, **options):
        consultants_data = [
            {
                'username': 'dr_ivanov',
                'first_name': 'Александр',
                'last_name': 'Иванов',
                'email': 'dr.ivanov@example.com',
                'specialization': 'pediatrician',
                'license_number': 'PED-001-2024',
                'experience_years': 15,
                'education': 'Кыргызская государственная медицинская академия, педиатрический факультет (2009)\nКурсы повышения квалификации по детской неврологии (2015)\nСертификат по грудному вскармливанию (2018)',
                'bio': 'Опытный педиатр с 15-летним стажем работы. Специализируюсь на лечении детей от 0 до 18 лет. Помогу с вопросами развития, питания, вакцинации и лечения детских заболеваний.',
                'consultation_fee': 500.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.8,
                'total_consultations': 245
            },
            {
                'username': 'dr_petrov',
                'first_name': 'Мария',
                'last_name': 'Петрова',
                'email': 'dr.petrov@example.com',
                'specialization': 'neurologist',
                'license_number': 'NEU-002-2024',
                'experience_years': 12,
                'education': 'Российский национальный исследовательский медицинский университет им. Н.И. Пирогова, неврологический факультет (2012)\nКурсы по детской неврологии (2014)\nСертификат по ЭЭГ диагностике (2016)',
                'bio': 'Детский невролог с большим опытом работы. Специализируюсь на диагностике и лечении неврологических заболеваний у детей, задержках развития, эпилепсии.',
                'consultation_fee': 600.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.9,
                'total_consultations': 189
            },
            {
                'username': 'dr_sidorova',
                'first_name': 'Елена',
                'last_name': 'Сидорова',
                'email': 'dr.sidorova@example.com',
                'specialization': 'nutritionist',
                'license_number': 'NUT-003-2024',
                'experience_years': 8,
                'education': 'Кыргызская государственная медицинская академия, диетологический факультет (2016)\nКурсы по детскому питанию (2017)\nСертификат по грудному вскармливанию (2019)',
                'bio': 'Специалист по детскому питанию. Помогу составить правильный рацион для вашего ребенка, решить проблемы с прикормом, аллергиями и пищевыми расстройствами.',
                'consultation_fee': 400.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.7,
                'total_consultations': 156
            },
            {
                'username': 'dr_kim',
                'first_name': 'Анна',
                'last_name': 'Ким',
                'email': 'dr.kim@example.com',
                'specialization': 'psychologist',
                'license_number': 'PSY-004-2024',
                'experience_years': 10,
                'education': 'Кыргызский национальный университет, факультет психологии (2014)\nКурсы по детской психологии (2015)\nСертификат по арт-терапии (2017)',
                'bio': 'Детский психолог с опытом работы с детьми разных возрастов. Помогу решить проблемы поведения, адаптации, страхов, тревожности и других психологических вопросов.',
                'consultation_fee': 450.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.6,
                'total_consultations': 134
            },
            {
                'username': 'dr_zhumabaeva',
                'first_name': 'Айгуль',
                'last_name': 'Жумабаева',
                'email': 'dr.zhumabaeva@example.com',
                'specialization': 'lactation',
                'license_number': 'LAC-005-2024',
                'experience_years': 6,
                'education': 'Кыргызская государственная медицинская академия, акушерство и гинекология (2018)\nСертификат консультанта по грудному вскармливанию (2019)\nКурсы по лактации (2020)',
                'bio': 'Консультант по грудному вскармливанию. Помогу решить проблемы с кормлением грудью, увеличить лактацию, правильно прикладывать ребенка к груди.',
                'consultation_fee': 300.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.8,
                'total_consultations': 98
            },
            {
                'username': 'dr_toktobaev',
                'first_name': 'Бакыт',
                'last_name': 'Токтобаев',
                'email': 'dr.toktobaev@example.com',
                'specialization': 'sleep',
                'license_number': 'SLE-006-2024',
                'experience_years': 7,
                'education': 'Кыргызская государственная медицинская академия, педиатрический факультет (2017)\nКурсы по детскому сну (2018)\nСертификат консультанта по сну (2019)',
                'bio': 'Специалист по детскому сну. Помогу наладить режим сна вашего ребенка, решить проблемы с засыпанием, ночными пробуждениями и другими нарушениями сна.',
                'consultation_fee': 350.00,
                'is_available': True,
                'is_verified': True,
                'rating': 4.5,
                'total_consultations': 87
            }
        ]

        created_count = 0
        for consultant_data in consultants_data:
            # Создаем пользователя
            user, user_created = User.objects.get_or_create(
                username=consultant_data['username'],
                defaults={
                    'first_name': consultant_data['first_name'],
                    'last_name': consultant_data['last_name'],
                    'email': consultant_data['email'],
                    'is_active': True,
                }
            )
            
            if user_created:
                user.set_password('consultant123')  # Простой пароль для тестирования
                user.save()
            
            # Создаем профиль консультанта
            consultant_profile, profile_created = ConsultantProfile.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': consultant_data['specialization'],
                    'license_number': consultant_data['license_number'],
                    'experience_years': consultant_data['experience_years'],
                    'education': consultant_data['education'],
                    'bio': consultant_data['bio'],
                    'consultation_fee': consultant_data['consultation_fee'],
                    'is_available': consultant_data['is_available'],
                    'is_verified': consultant_data['is_verified'],
                    'rating': consultant_data['rating'],
                    'total_consultations': consultant_data['total_consultations'],
                }
            )
            
            if profile_created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан консультант: {consultant_profile.full_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Консультант уже существует: {consultant_profile.full_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} новых консультантов')
        )
        self.stdout.write(
            self.style.WARNING('Пароли для всех консультантов: consultant123')
        )




