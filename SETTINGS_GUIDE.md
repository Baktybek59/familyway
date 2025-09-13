# ⚙️ Руководство по настройкам FamilyWay +

## 📁 Структура настроек

Теперь проект использует **единый файл настроек** `settings.py` с поддержкой разных окружений.

### 🔄 Переменная окружения `ENVIRONMENT`

- **`development`** - режим разработки (по умолчанию)
- **`production`** - продакшн режим

## 🛠️ Настройка окружения

### 1. **Через .env файл (рекомендуется)**
```bash
# Создание .env файла
cp env.example .env

# Редактирование .env
nano .env
```

**Содержимое .env:**
```env
# Окружение
ENVIRONMENT=production

# Django настройки
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=familyway.plus,www.familyway.plus

# База данных MySQL
DB_NAME=baybyway_production
DB_USER=user_bayby1
DB_PASSWORD=J@nym9494!
DB_HOST=localhost
DB_PORT=3306

# Email настройки
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 2. **Через переменные окружения**
```bash
# Для разработки
export ENVIRONMENT=development
python manage.py runserver

# Для продакшена
export ENVIRONMENT=production
gunicorn --bind 0.0.0.0:8000 baybyway.wsgi:application
```

### 3. **Автоматическое переключение**
```bash
# Переключение на продакшн
./switch_environment.sh production

# Переключение на разработку
./switch_environment.sh development
```

## 🔧 Различия между окружениями

### **Development (Разработка)**
- `DEBUG = True`
- База данных: `baybyway_dev`
- Статические файлы: локальная разработка
- Логирование: консоль
- Безопасность: минимальная

### **Production (Продакшн)**
- `DEBUG = False`
- База данных: `baybyway_production`
- Статические файлы: WhiteNoise + сжатие
- Логирование: файлы + консоль
- Безопасность: максимальная
- HTTPS: принудительный редирект
- HSTS: включен
- Заголовки безопасности: все включены

## 🚀 Запуск приложения

### **Разработка**
```bash
# Обычный запуск
python manage.py runserver

# С явным указанием окружения
ENVIRONMENT=development python manage.py runserver

# Через скрипт
./start_server.sh
```

### **Продакшн**
```bash
# Через Gunicorn
ENVIRONMENT=production gunicorn --bind 0.0.0.0:8000 baybyway.wsgi:application

# Через скрипт
./start_production.sh

# Через systemd
sudo systemctl start familyway
sudo systemctl enable familyway
```

## 📊 Настройки базы данных

### **MySQL конфигурация**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='baybyway_production'),
        'USER': config('DB_USER', default='user_bayby1'),
        'PASSWORD': config('DB_PASSWORD', default='J@nym9494!'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### **Создание баз данных**
```bash
# Создание базы для разработки
mysql -u root -e "CREATE DATABASE baybyway_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Создание базы для продакшена
mysql -u root -e "CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## 🔒 Настройки безопасности

### **Production только**
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = 31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- `SECURE_HSTS_PRELOAD = True`
- `X_FRAME_OPTIONS = 'DENY'`
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`

## 📝 Логирование

### **Development**
- Логи в консоль
- Уровень: DEBUG

### **Production**
- Логи в файл: `logs/django.log`
- Логи в консоль
- Уровень: INFO
- Ротация логов

## 🗂️ Статические файлы

### **Development**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### **Production**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🧪 Тестирование настроек

### **Проверка конфигурации**
```bash
# Проверка настроек Django
python manage.py check

# Проверка миграций
python manage.py showmigrations

# Проверка подключения к БД
python manage.py dbshell
```

### **Проверка окружения**
```python
# В Python shell
from django.conf import settings
print(f"Environment: {settings.ENVIRONMENT}")
print(f"DEBUG: {settings.DEBUG}")
print(f"Database: {settings.DATABASES['default']['NAME']}")
```

## 🔧 Полезные команды

### **Управление окружениями**
```bash
# Переключение окружения
./switch_environment.sh production
./switch_environment.sh development

# Проверка текущего окружения
grep ENVIRONMENT .env
```

### **Управление базой данных**
```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic
```

### **Управление сервисом**
```bash
# Запуск сервиса
sudo systemctl start familyway

# Остановка сервиса
sudo systemctl stop familyway

# Перезапуск сервиса
sudo systemctl restart familyway

# Статус сервиса
sudo systemctl status familyway

# Логи сервиса
sudo journalctl -u familyway -f
```

## 📋 Миграция с старой структуры

Если у вас была старая структура с `settings_production.py`:

1. **Удалите старые файлы:**
   ```bash
   rm baybyway/settings_production.py
   ```

2. **Обновите .env:**
   ```bash
   echo "ENVIRONMENT=production" >> .env
   ```

3. **Обновите скрипты:**
   ```bash
   # Замените в скриптах
   # DJANGO_SETTINGS_MODULE=baybyway.settings_production
   # на
   # ENVIRONMENT=production
   ```

## 🎯 Рекомендации

### **Для разработки**
- Используйте `ENVIRONMENT=development`
- Включите `DEBUG=True`
- Используйте отдельную БД для разработки

### **Для продакшена**
- Используйте `ENVIRONMENT=production`
- Отключите `DEBUG=False`
- Настройте HTTPS
- Используйте сильный SECRET_KEY
- Настройте мониторинг логов

---

**🎉 Теперь FamilyWay + использует единый файл настроек с поддержкой разных окружений!**
