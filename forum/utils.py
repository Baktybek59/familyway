import re
from django.contrib.auth.models import User


def extract_quoted_users_from_content(content: str) -> list:
    """
    Извлекает список пользователей, которые были процитированы в сообщении.
    Ищет BBCode цитаты вида [quote=username]content[/quote]
    """
    if not content:
        return []
    
    # Паттерн для поиска BBCode цитат [quote=username]content[/quote]
    quote_pattern = r'\[quote=([^\]]+)\].*?\[/quote\]'
    
    # Находим все цитаты
    quotes = re.findall(quote_pattern, content, re.DOTALL | re.IGNORECASE)
    
    # Получаем уникальных пользователей
    quoted_usernames = list(set(quotes))
    
    # Проверяем, что пользователи существуют
    quoted_users = []
    for username in quoted_usernames:
        try:
            user = User.objects.get(username=username.strip())
            quoted_users.append(user)
        except User.DoesNotExist:
            # Пользователь не найден, пропускаем
            continue
    
    return quoted_users


def extract_mentioned_users_from_content(content: str) -> list:
    """
    Извлекает список пользователей, которые были упомянуты в сообщении.
    Ищет упоминания вида @username
    """
    if not content:
        return []
    
    # Паттерн для поиска упоминаний @username
    mention_pattern = r'@(\w+)'
    
    # Находим все упоминания
    mentions = re.findall(mention_pattern, content)
    
    # Получаем уникальных пользователей
    mentioned_usernames = list(set(mentions))
    
    # Проверяем, что пользователи существуют
    mentioned_users = []
    for username in mentioned_usernames:
        try:
            user = User.objects.get(username=username.strip())
            mentioned_users.append(user)
        except User.DoesNotExist:
            # Пользователь не найден, пропускаем
            continue
    
    return mentioned_users

