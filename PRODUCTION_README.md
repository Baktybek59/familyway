# BaybyWay Production Setup (Native Installation)

## 🚀 Быстрый старт (без Docker)

### 1. Установка зависимостей

```bash
# Установка Python зависимостей
pip install -r requirements.txt

# Установка MySQL (Ubuntu/Debian)
sudo apt update
sudo apt install mysql-server mysql-client libmysqlclient-dev

# Установка nginx (опционально)
sudo apt install nginx
```

### 2. Настройка базы данных

```bash
# Запуск скрипта настройки MySQL
python setup_mysql.py
```

### 3. Деплой приложения

```bash
# Запуск скрипта деплоя
python deploy.py
```

### 4. Запуск сервера

```bash
# Запуск с Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 baybyway.wsgi_production:application

# Или с systemd (после настройки)
sudo systemctl enable baybyway
sudo systemctl start baybyway
```

## 📋 Конфигурация

### База данных
- **Название**: `baybyway_production`
- **Пользователь**: `baybyway_user`
- **Пароль**: `J@nym9494!`
- **Хост**: `localhost:3306`

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-super-secret-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Nginx конфигурация

1. Скопируйте `nginx_baybyway.conf` в `/etc/nginx/sites-available/`
2. Создайте символическую ссылку:
   ```bash
   sudo ln -s /etc/nginx/sites-available/nginx_baybyway.conf /etc/nginx/sites-enabled/
   ```
3. Перезапустите nginx:
   ```bash
   sudo systemctl restart nginx
   ```

## 🔧 Управление сервисом

```bash
# Статус сервиса
sudo systemctl status baybyway

# Запуск сервиса
sudo systemctl start baybyway

# Остановка сервиса
sudo systemctl stop baybyway

# Перезапуск сервиса
sudo systemctl restart baybyway

# Просмотр логов
sudo journalctl -u baybyway -f
```

## 📁 Структура файлов

```
baybyway/
├── settings_production.py    # Настройки продакшена
├── wsgi_production.py        # WSGI для продакшена
├── baybyway.service          # Systemd сервис
├── nginx_baybyway.conf       # Nginx конфигурация
├── setup_mysql.py            # Скрипт настройки MySQL
├── deploy.py                 # Скрипт деплоя
└── requirements.txt          # Python зависимости
```

## 🔒 Безопасность

- Измените `SECRET_KEY` в продакшене
- Настройте SSL сертификаты для HTTPS
- Ограничьте доступ к базе данных
- Регулярно обновляйте зависимости
- Настройте бэкапы базы данных

## 📊 Мониторинг

- Логи приложения: `logs/django.log`
- Логи nginx: `/var/log/nginx/`
- Логи systemd: `sudo journalctl -u baybyway`

## 🆘 Устранение неполадок

### Проблемы с базой данных
```bash
# Проверка подключения
mysql -u baybyway_user -p baybyway_production

# Сброс пароля пользователя
mysql -u root -p
ALTER USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';
FLUSH PRIVILEGES;
```

### Проблемы с правами доступа
```bash
# Установка правильных прав
sudo chown -R www-data:www-data /home/gurusan/Документы/baybyWay
sudo chmod -R 755 /home/gurusan/Документы/baybyWay
```

### Проблемы с статическими файлами
```bash
# Пересборка статических файлов
python manage.py collectstatic --noinput --settings=baybyway.settings_production
```
