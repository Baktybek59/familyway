from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from support.models import SupportProfile


class Command(BaseCommand):
    help = 'Создает сотрудника техподдержки'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Имя пользователя')
        parser.add_argument('--email', type=str, help='Email')
        parser.add_argument('--password', type=str, help='Пароль')
        parser.add_argument('--first-name', type=str, help='Имя')
        parser.add_argument('--last-name', type=str, help='Фамилия')
        parser.add_argument('--employee-id', type=str, help='ID сотрудника')
        parser.add_argument('--department', type=str, help='Отдел')
        parser.add_argument('--phone', type=str, help='Телефон')

    def handle(self, *args, **options):
        username = options['username'] or 'support_admin'
        email = options['email'] or 'support@baybyway.com'
        password = options['password'] or 'support123'
        first_name = options['first_name'] or 'Администратор'
        last_name = options['last_name'] or 'Техподдержки'
        employee_id = options['employee_id'] or 'SUP001'
        department = options['department'] or 'Техподдержка'
        phone = options['phone'] or '+996 555 123 456'

        # Создаем пользователя
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Пользователь {username} создан')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Пользователь {username} уже существует')
            )

        # Создаем профиль техподдержки
        profile, created = SupportProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': employee_id,
                'department': department,
                'phone': phone,
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Профиль техподдержки для {username} создан')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Профиль техподдержки для {username} уже существует')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Сотрудник техподдержки создан:\n'
                f'  Логин: {username}\n'
                f'  Пароль: {password}\n'
                f'  ID сотрудника: {employee_id}\n'
                f'  Отдел: {department}\n'
                f'  Телефон: {phone}'
            )
        )




