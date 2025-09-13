# 🚀 BaybyWay - Нативная установка (без Docker)

## 📋 Обзор

Этот проект использует **нативную установку** - все сервисы запускаются напрямую на сервере без использования Docker контейнеров.

## 🎯 Преимущества нативной установки

- ✅ **Простота** - не требует изучения Docker
- ✅ **Производительность** - нет накладных расходов контейнеризации
- ✅ **Контроль** - полный доступ к системным ресурсам
- ✅ **Отладка** - проще диагностировать проблемы
- ✅ **Обслуживание** - стандартные Linux команды

## 💻 Системные требования

### Минимальные требования:
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: 1GB (рекомендуется 2GB+)
- **CPU**: 1 ядро (рекомендуется 2+)
- **Storage**: 10GB свободного места
- **Python**: 3.8+ (рекомендуется 3.12+)
- **MySQL**: 8.0+ (рекомендуется 8.0+)

## 🔧 Установка зависимостей

### Ubuntu/Debian:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Установка MySQL
sudo apt install mysql-server mysql-client libmysqlclient-dev -y

# Установка Nginx (опционально)
sudo apt install nginx -y

# Установка дополнительных инструментов
sudo apt install git curl wget htop -y
```

### CentOS/RHEL:
```bash
# Обновление системы
sudo yum update -y

# Установка Python и зависимостей
sudo yum install python3 python3-pip python3-devel -y

# Установка MySQL
sudo yum install mysql-server mysql-devel -y

# Установка Nginx (опционально)
sudo yum install nginx -y

# Установка дополнительных инструментов
sudo yum install git curl wget htop -y
```

## 🗄️ Настройка MySQL

### 1. Запуск MySQL
```bash
# Ubuntu/Debian
sudo systemctl start mysql
sudo systemctl enable mysql

# CentOS/RHEL
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### 2. Безопасная настройка
```bash
# Запуск безопасной настройки
sudo mysql_secure_installation
```

### 3. Создание базы данных
```bash
# Подключение к MySQL
sudo mysql -u root -p

# Создание базы данных
CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Создание пользователя
CREATE USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';

# Предоставление прав
GRANT ALL PRIVILEGES ON baybyway_production.* TO 'baybyway_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 🐍 Настройка Python окружения

### 1. Создание виртуального окружения
```bash
# Переход в директорию проекта
cd /path/to/baybyway

# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate
```

### 2. Установка зависимостей
```bash
# Установка из requirements.txt
pip install -r requirements.txt

# Или установка по отдельности
pip install Django==5.2.6
pip install mysqlclient==2.2.4
pip install gunicorn==23.0.0
pip install whitenoise==6.8.2
```

## 🚀 Запуск приложения

### 1. Автоматический запуск
```bash
# Запуск скрипта
./start_production.sh
```

### 2. Ручной запуск
```bash
# Активация окружения
source venv/bin/activate

# Запуск миграций
python manage.py migrate --settings=baybyway.settings_production

# Сбор статических файлов
python manage.py collectstatic --noinput --settings=baybyway.settings_production

# Запуск сервера
gunicorn --workers 3 --bind 0.0.0.0:8000 baybyway.wsgi_production:application
```

## 🌐 Настройка Nginx (опционально)

### 1. Копирование конфигурации
```bash
# Копирование конфигурации
sudo cp nginx_baybyway.conf /etc/nginx/sites-available/

# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/nginx_baybyway.conf /etc/nginx/sites-enabled/

# Удаление дефолтной конфигурации
sudo rm /etc/nginx/sites-enabled/default
```

### 2. Перезапуск Nginx
```bash
# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔧 Настройка Systemd сервиса

### 1. Копирование сервиса
```bash
# Копирование файла сервиса
sudo cp baybyway.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload
```

### 2. Запуск сервиса
```bash
# Включение автозапуска
sudo systemctl enable baybyway

# Запуск сервиса
sudo systemctl start baybyway

# Проверка статуса
sudo systemctl status baybyway
```

## 📊 Мониторинг и логи

### Просмотр логов
```bash
# Логи приложения
tail -f logs/django.log

# Логи systemd
sudo journalctl -u baybyway -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Мониторинг ресурсов
```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Сетевые соединения
netstat -tlnp | grep :8000
```

## 🔒 Безопасность

### 1. Настройка файрвола
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. Настройка SSL (Let's Encrypt)
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com
```

## 🆘 Устранение неполадок

### Проблемы с MySQL
```bash
# Проверка статуса
sudo systemctl status mysql

# Перезапуск
sudo systemctl restart mysql

# Проверка подключения
mysql -u baybyway_user -p baybyway_production
```

### Проблемы с Python
```bash
# Проверка версии Python
python3 --version

# Проверка виртуального окружения
which python
pip list
```

### Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tlnp | grep :8000

# Освобождение порта
sudo fuser -k 8000/tcp
```

## 📈 Оптимизация производительности

### 1. Настройка MySQL
```sql
-- В /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
max_connections = 100
```

### 2. Настройка Gunicorn
```bash
# Запуск с большим количеством воркеров
gunicorn --workers 4 --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:8000 baybyway.wsgi_production:application
```

### 3. Настройка Nginx
```nginx
# В nginx конфигурации
worker_processes auto;
worker_connections 1024;

# Gzip сжатие
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## ✅ Проверка установки

После завершения установки проверьте:

1. ✅ MySQL запущен и доступен
2. ✅ Python окружение активировано
3. ✅ Django приложение запускается
4. ✅ Статические файлы собираются
5. ✅ Nginx проксирует запросы (если настроен)
6. ✅ Systemd сервис работает (если настроен)

## 🎉 Готово!

Ваш BaybyWay проект готов к работе в продакшене с нативной установкой!

**Преимущества этого подхода:**
- Простота развертывания
- Лучшая производительность
- Полный контроль над системой
- Легкое обслуживание


