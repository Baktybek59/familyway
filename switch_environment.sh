#!/bin/bash

# Скрипт для переключения между окружениями FamilyWay +
# Использование: ./switch_environment.sh [development|production]

set -e

ENVIRONMENT=${1:-development}

if [ "$ENVIRONMENT" != "development" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "❌ Ошибка: Неверное окружение. Используйте 'development' или 'production'"
    echo "Использование: ./switch_environment.sh [development|production]"
    exit 1
fi

echo "🔄 Переключение на окружение: $ENVIRONMENT"
echo "========================================"

# Обновление .env файла
if [ -f ".env" ]; then
    echo "📝 Обновление .env файла..."
    sed -i "s/ENVIRONMENT=.*/ENVIRONMENT=$ENVIRONMENT/" .env
    
    if [ "$ENVIRONMENT" = "production" ]; then
        sed -i "s/DEBUG=.*/DEBUG=False/" .env
        echo "  ✅ DEBUG=False для продакшена"
    else
        sed -i "s/DEBUG=.*/DEBUG=True/" .env
        echo "  ✅ DEBUG=True для разработки"
    fi
else
    echo "❌ Файл .env не найден. Создайте его из env.example"
    exit 1
fi

# Проверка настроек
echo "🔍 Проверка настроек Django..."
python manage.py check

echo ""
echo "✅ Переключение на $ENVIRONMENT завершено!"
echo ""
echo "📋 Текущие настройки:"
echo "   Окружение: $ENVIRONMENT"
echo "   DEBUG: $(grep DEBUG .env | cut -d'=' -f2)"
echo "   База данных: $(grep DB_NAME .env | cut -d'=' -f2)"
echo ""
echo "🚀 Для запуска сервера:"
if [ "$ENVIRONMENT" = "production" ]; then
    echo "   Продакшн: ./start_production.sh"
    echo "   Или: gunicorn --bind 0.0.0.0:8000 baybyway.wsgi:application"
else
    echo "   Разработка: python manage.py runserver"
    echo "   Или: ./start_server.sh"
fi
