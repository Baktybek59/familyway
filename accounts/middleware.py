from django.shortcuts import redirect
from django.urls import reverse
from .utils import get_user_redirect_url


class UserRedirectMiddleware:
    """Middleware для перенаправления пользователей на соответствующие дашборды после авторизации"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Проверяем, если пользователь авторизован и находится на главной странице
        if (request.user.is_authenticated and 
            request.path == '/' and  # Перенаправляем только с главной страницы
            not request.GET.get('next')):  # Не перенаправляем если есть параметр next
            
            redirect_url = get_user_redirect_url(request.user)
            if redirect_url:
                return redirect(redirect_url)
        
        return response
