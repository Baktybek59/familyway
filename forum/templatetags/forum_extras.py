from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def bbcode_to_html(text):
    """Конвертирует BBCode в HTML"""
    if not text:
        return text
    
    # Обработка цитат [quote=username]content[/quote]
    def replace_quote(match):
        username = match.group(1) or 'Anonymous'
        content = match.group(2)
        return f'''
        <div class="quote-block">
            <div class="quote-author">@{username}</div>
            <div class="quote-content">{content}</div>
        </div>
        '''
    
    # Обработка упоминаний @username
    def replace_mention(match):
        username = match.group(1)
        return f'<a href="#" class="mention-link">@{username}</a>'
    
    # Применяем преобразования
    text = re.sub(r'\[quote=([^\]]*)\](.*?)\[/quote\]', replace_quote, text, flags=re.DOTALL)
    text = re.sub(r'@(\w+)', replace_mention, text)
    
    # Конвертируем переносы строк в <br>
    text = text.replace('\n', '<br>')
    
    return mark_safe(text)

@register.filter
def get_reply_level(post):
    """Возвращает уровень вложенности ответа"""
    level = 0
    current_post = post
    while current_post.parent_post:
        level += 1
        current_post = current_post.parent_post
        if level >= 5:  # Максимум 5 уровней
            break
    return level


