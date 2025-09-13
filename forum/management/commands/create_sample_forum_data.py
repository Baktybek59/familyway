from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import ForumCategory, Topic, Post
from accounts.models import ParentProfile, Family
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = 'Создает примеры категорий, тем и сообщений для форума'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Создание категорий форума...'))
        
        # Создаем категории
        categories_data = [
            {
                'name': _('Здоровье ребенка'),
                'description': _('Вопросы здоровья, развития, болезней и лечения детей'),
                'icon': 'bi-heart-pulse',
                'color': '#ff6b9d',
                'order': 1
            },
            {
                'name': _('Питание и кормление'),
                'description': _('Грудное вскармливание, прикорм, детское питание'),
                'icon': 'bi-cup-hot',
                'color': '#4ecdc4',
                'order': 2
            },
            {
                'name': _('Развитие и воспитание'),
                'description': _('Физическое и психическое развитие, воспитательные вопросы'),
                'icon': 'bi-people',
                'color': '#ffe66d',
                'order': 3
            },
            {
                'name': _('Сон и режим'),
                'description': _('Налаживание сна, режим дня, проблемы со сном'),
                'icon': 'bi-moon',
                'color': '#a8e6cf',
                'order': 4
            },
            {
                'name': _('Игрушки и развлечения'),
                'description': _('Выбор игрушек, развивающие игры, развлечения'),
                'icon': 'bi-joystick',
                'color': '#ffd93d',
                'order': 5
            },
            {
                'name': _('Безопасность'),
                'description': _('Безопасность дома, на улице, в путешествиях'),
                'icon': 'bi-shield-check',
                'color': '#ff8a80',
                'order': 6
            }
        ]

        created_categories = []
        for cat_data in categories_data:
            category, created = ForumCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'order': cat_data['order'],
                    'is_active': True
                }
            )
            if created:
                created_categories.append(category)
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Категория уже существует: {category.name}'))

        self.stdout.write(self.style.SUCCESS('Создание тестовых тем...'))
        
        # Получаем или создаем тестовых пользователей
        test_users = []
        for i in range(1, 6):
            username = f'parent{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Родитель{i}',
                    'last_name': 'Тестовый'
                }
            )
            if created:
                user.set_password('parent123')
                user.save()
                # Создаем профиль родителя
                ParentProfile.objects.create(
                    user=user,
                    user_type='parent',
                    role='mom' if i % 2 == 0 else 'dad',
                    child_name=f'Ребенок{i}',
                    child_birth_date='2023-01-01'
                )
            test_users.append(user)

        # Создаем темы
        topics_data = [
            {
                'title': _('Ребенок не хочет есть овощи'),
                'content': _('Моему сыну 2 года, и он категорически отказывается есть любые овощи. Пробовали разные способы приготовления, но ничего не помогает. Может быть, у кого-то есть проверенные рецепты или советы?'),
                'category': _('Питание и кормление'),
                'author': 'parent1'
            },
            {
                'title': _('Проблемы со сном у 8-месячного ребенка'),
                'content': _('Дочка просыпается каждые 2-3 часа ночью и требует грудь. Днем спит только на руках. Уже не знаю, что делать. Помогите советом!'),
                'category': _('Сон и режим'),
                'author': 'parent2'
            },
            {
                'title': _('Когда начинать прикорм?'),
                'content': _('Педиатр говорит начинать в 6 месяцев, а бабушка настаивает на 4. Ребенку сейчас 5 месяцев, он на ГВ. Когда лучше начать и с чего?'),
                'category': _('Питание и кормление'),
                'author': 'parent3'
            },
            {
                'title': _('Ребенок не говорит в 2 года'),
                'content': _('Сыну 2 года и 3 месяца, а он говорит только несколько слов. Сверстники уже строят предложения. Стоит ли беспокоиться?'),
                'category': _('Развитие и воспитание'),
                'author': 'parent4'
            },
            {
                'title': _('Как обезопасить квартиру для малыша?'),
                'content': _('Ребенок начал ползать и везде лезет. Какие меры безопасности нужно принять? Что купить в первую очередь?'),
                'category': _('Безопасность'),
                'author': 'parent5'
            },
            {
                'title': _('Температура 38.5 у ребенка'),
                'content': _('У дочки поднялась температура 38.5, больше никаких симптомов нет. Стоит ли вызывать врача или можно подождать?'),
                'category': _('Здоровье ребенка'),
                'author': 'parent1'
            },
            {
                'title': _('Какие игрушки выбрать для 1 года?'),
                'content': _('Сыну скоро год, хочу подарить развивающие игрушки. Что посоветуете? Какие действительно полезны для развития?'),
                'category': _('Игрушки и развлечения'),
                'author': 'parent2'
            },
            {
                'title': _('Ребенок кусается в детском саду'),
                'content': _('Воспитатель жалуется, что мой сын кусает других детей. Дома такого не замечала. Как отучить?'),
                'category': _('Развитие и воспитание'),
                'author': 'parent3'
            }
        ]

        created_topics = []
        for topic_data in topics_data:
            # Находим категорию
            category = ForumCategory.objects.get(name=topic_data['category'])
            # Находим автора
            author = User.objects.get(username=topic_data['author'])
            
            topic, created = Topic.objects.get_or_create(
                title=topic_data['title'],
                defaults={
                    'content': topic_data['content'],
                    'category': category,
                    'author': author,
                    'status': 'open',
                    'is_active': True,
                    'views_count': 0,
                    'likes_count': 0
                }
            )
            if created:
                created_topics.append(topic)
                self.stdout.write(self.style.SUCCESS(f'Создана тема: {topic.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Тема уже существует: {topic.title}'))

        self.stdout.write(self.style.SUCCESS('Создание тестовых сообщений...'))
        
        # Создаем сообщения для тем
        sample_posts = [
            {
                'topic_title': _('Ребенок не хочет есть овощи'),
                'content': _('Попробуйте делать овощные пюре с фруктами. Мой сын ел морковное пюре с яблоком.'),
                'author': 'parent2'
            },
            {
                'topic_title': _('Ребенок не хочет есть овощи'),
                'content': _('А мы делали овощи в виде фигурок - морковные звездочки, огурчики-кружочки. Детям нравится играть с едой.'),
                'author': 'parent3'
            },
            {
                'topic_title': _('Проблемы со сном у 8-месячного ребенка'),
                'content': _('У нас была похожая ситуация. Помогло введение ритуала перед сном и постепенное отучение от засыпания на руках.'),
                'author': 'parent1'
            },
            {
                'topic_title': _('Когда начинать прикорм?'),
                'content': _('ВОЗ рекомендует начинать прикорм в 6 месяцев. Начните с овощных пюре - кабачок, брокколи.'),
                'author': 'parent4'
            },
            {
                'topic_title': _('Ребенок не говорит в 2 года'),
                'content': _('Не паникуйте! Мальчики часто начинают говорить позже. Но консультация логопеда не помешает.'),
                'author': 'parent5'
            },
            {
                'topic_title': _('Как обезопасить квартиру для малыша?'),
                'content': _('Обязательно: заглушки на розетки, блокировка дверей, защита углов, ворота безопасности.'),
                'author': 'parent1'
            },
            {
                'topic_title': _('Температура 38.5 у ребенка'),
                'content': _('При такой температуре лучше вызвать врача, особенно если ребенку меньше 3 лет.'),
                'author': 'parent2'
            },
            {
                'topic_title': _('Какие игрушки выбрать для 1 года?'),
                'content': _('Кубики, пирамидки, сортеры, музыкальные игрушки. Главное - безопасность и соответствие возрасту.'),
                'author': 'parent3'
            }
        ]

        created_posts = 0
        for post_data in sample_posts:
            try:
                topic = Topic.objects.get(title=post_data['topic_title'])
                author = User.objects.get(username=post_data['author'])
                
                post, created = Post.objects.get_or_create(
                    topic=topic,
                    author=author,
                    content=post_data['content'],
                    defaults={
                        'is_solution': False,
                        'likes_count': 0
                    }
                )
                if created:
                    created_posts += 1
                    self.stdout.write(self.style.SUCCESS(f'Создано сообщение в теме: {topic.title}'))
            except Topic.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Тема не найдена: {post_data["topic_title"]}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Пользователь не найден: {post_data["author"]}'))

        self.stdout.write(self.style.SUCCESS(f'Успешно создано:'))
        self.stdout.write(self.style.SUCCESS(f'- {len(created_categories)} категорий'))
        self.stdout.write(self.style.SUCCESS(f'- {len(created_topics)} тем'))
        self.stdout.write(self.style.SUCCESS(f'- {created_posts} сообщений'))
        self.stdout.write(self.style.WARNING('Пароли для тестовых пользователей: parent123'))




