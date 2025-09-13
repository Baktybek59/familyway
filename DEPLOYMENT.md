# Развертывание FamilyWay + на продакшн сервере

## Описание
FamilyWay + - это платформа для семей с детьми, включающая трекер развития, форум, блог и консультации специалистов.

## Домен
- **Основной домен**: familyway.plus
- **WWW домен**: www.familyway.plus
- **Поддомены**: *.familyway.plus

## Требования к серверу

### Минимальные требования:
- **ОС**: Ubuntu 20.04+ или CentOS 8+
- **RAM**: 2GB (рекомендуется 4GB+)
- **CPU**: 2 ядра (рекомендуется 4+)
- **Диск**: 20GB (рекомендуется 50GB+)
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Nginx**: 1.18+

## Установка

### 1. Подготовка сервера

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

# Создаем пользователя для приложения
sudo useradd -m -s /bin/bash familyplus
sudo usermod -aG www-data familyplus
```

### 2. Настройка базы данных

```bash
# Переключаемся на пользователя postgres
sudo -u postgres psql

# Создаем базу данных и пользователя
CREATE DATABASE family_plus;
CREATE USER family_plus_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE family_plus TO family_plus_user;
\q
```

### 3. Развертывание приложения

```bash
# Переключаемся на пользователя приложения
sudo su - familyplus

# Клонируем репозиторий
git clone https://github.com/your-username/family-plus.git
cd family-plus

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Копируем файл переменных окружения
cp env.example .env
nano .env  # Заполните реальными значениями

# Применяем миграции
python manage.py migrate

# Создаем суперпользователя
python manage.py createsuperuser

# Собираем статические файлы
python manage.py collectstatic --noinput
```

### 4. Настройка Gunicorn

```bash
# Копируем systemd сервис
sudo cp family-plus.service /etc/systemd/system/

# Перезагружаем systemd
sudo systemctl daemon-reload

# Запускаем сервис
sudo systemctl enable family-plus
sudo systemctl start family-plus

# Проверяем статус
sudo systemctl status family-plus
```

### 5. Настройка Nginx

```bash
# Копируем конфигурацию Nginx
sudo cp nginx.conf /etc/nginx/sites-available/familyway.plus

# Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/familyway.plus /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
```

### 6. Настройка SSL (Let's Encrypt)

#### Автоматическая настройка (рекомендуется):
```bash
# Запускаем автоматический скрипт настройки SSL
sudo chmod +x setup_ssl.sh
sudo ./setup_ssl.sh
```

#### Ручная настройка:
```bash
# Устанавливаем Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получаем SSL сертификат
sudo certbot --nginx -d familyway.plus -d www.familyway.plus

# Проверяем автообновление
sudo certbot renew --dry-run
```

#### Проверка безопасности HTTPS:
```bash
# Запускаем проверку безопасности
chmod +x check_https_security.sh
./check_https_security.sh
```

## Обновление

```bash
# Переключаемся на пользователя приложения
sudo su - familyplus
cd family-plus

# Обновляем код
git pull origin main

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем новые зависимости
pip install -r requirements.txt

# Применяем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Перезапускаем сервисы
sudo systemctl restart family-plus
sudo systemctl restart nginx
```

## Мониторинг

### Логи приложения
```bash
# Логи Gunicorn
sudo journalctl -u family-plus -f

# Логи Nginx
sudo tail -f /var/log/nginx/familyway.plus.access.log
sudo tail -f /var/log/nginx/familyway.plus.error.log
```

### Мониторинг ресурсов
```bash
# Использование диска
df -h

# Использование памяти
free -h

# Процессы
htop
```

## Безопасность

### Firewall
```bash
# Настраиваем UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Резервное копирование
```bash
# Создаем скрипт бэкапа
sudo nano /usr/local/bin/backup-family-plus.sh

#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/family-plus"
mkdir -p $BACKUP_DIR

# Бэкап базы данных
pg_dump family_plus > $BACKUP_DIR/db_$DATE.sql

# Бэкап медиа файлов
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/familyplus/family-plus/media/

# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Делаем скрипт исполняемым
sudo chmod +x /usr/local/bin/backup-family-plus.sh

# Добавляем в crontab (ежедневно в 2:00)
sudo crontab -e
# Добавить строку: 0 2 * * * /usr/local/bin/backup-family-plus.sh
```

## Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь, что все сервисы запущены
3. Проверьте конфигурацию Nginx
4. Проверьте права доступа к файлам

## Контакты

- **Email**: support@familyway.plus
- **Документация**: https://familyway.plus/docs
- **Статус**: https://status.familyway.plus



