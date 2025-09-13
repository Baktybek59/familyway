#!/bin/bash

# Полный скрипт настройки FamilyWay + с MySQL
# Использование: sudo ./setup_familyway_mysql.sh

set -e

echo "🚀 Полная настройка FamilyWay + с MySQL"
echo "======================================"

# Переменные
DB_NAME="baybyway_production"
DB_USER="user_bayby1"
DB_PASSWORD="J@nym9494!"
PROJECT_DIR="/home/gurusan/Документы/baybyWay"

# Проверка прав администратора
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: Запустите скрипт с правами администратора (sudo)"
    exit 1
fi

echo "📋 Информация о проекте:"
echo "   Проект: FamilyWay +"
echo "   Директория: $PROJECT_DIR"
echo "   База данных: $DB_NAME"
echo "   Пользователь БД: $DB_USER"
echo ""

# Переход в директорию проекта
cd $PROJECT_DIR

# 1. Установка MySQL
echo "🗄️  Шаг 1: Установка и настройка MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "📦 Установка MySQL Server..."
    apt update
    apt install -y mysql-server mysql-client
    
    # Запуск MySQL
    systemctl start mysql
    systemctl enable mysql
else
    echo "✅ MySQL уже установлен"
fi

# 2. Настройка базы данных
echo "🔧 Шаг 2: Настройка базы данных..."
mysql -u root -e "
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
"

# 3. Установка Python зависимостей
echo "🐍 Шаг 3: Установка Python зависимостей..."
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

# Активация виртуального окружения
if [ -d "venv" ]; then
    echo "✅ Виртуальное окружение найдено"
    source venv/bin/activate
else
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 4. Настройка Django
echo "⚙️  Шаг 4: Настройка Django..."

# Создание .env файла
if [ ! -f ".env" ]; then
    echo "📝 Создание .env файла..."
    cp env.example .env
    
    # Обновление .env с правильными настройками
    sed -i "s/ENVIRONMENT=.*/ENVIRONMENT=production/" .env
    sed -i "s/DB_NAME=.*/DB_NAME=$DB_NAME/" .env
    sed -i "s/DB_USER=.*/DB_USER=$DB_USER/" .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
    sed -i "s/DB_HOST=.*/DB_HOST=localhost/" .env
    sed -i "s/DB_PORT=.*/DB_PORT=3306/" .env
    sed -i "s/DEBUG=.*/DEBUG=False/" .env
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')/" .env
else
    echo "✅ .env файл уже существует"
fi

# 5. Миграции Django
echo "🔄 Шаг 5: Выполнение миграций Django..."

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# 6. Создание суперпользователя
echo "👤 Шаг 6: Создание суперпользователя..."
echo "Введите данные для суперпользователя:"
python manage.py createsuperuser

# 7. Сбор статических файлов
echo "📁 Шаг 7: Сбор статических файлов..."
python manage.py collectstatic --noinput

# 8. Создание скриптов управления
echo "📝 Шаг 8: Создание скриптов управления..."

# Скрипт запуска сервера
cat > start_server.sh << 'EOF'
#!/bin/bash
cd /home/gurusan/Документы/baybyWay
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
EOF

# Скрипт запуска в продакшене
cat > start_production.sh << 'EOF'
#!/bin/bash
cd /home/gurusan/Документы/baybyWay
source venv/bin/activate
export ENVIRONMENT=production
gunicorn --bind 0.0.0.0:8000 baybyway.wsgi:application
EOF

# Скрипт бэкапа
cat > backup_database.sh << 'EOF'
#!/bin/bash
DB_NAME="baybyway_production"
DB_USER="user_bayby1"
DB_PASSWORD="J@nym9494!"
BACKUP_DIR="/home/gurusan/Документы/baybyWay/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/familyway_backup_$DATE.sql
gzip $BACKUP_DIR/familyway_backup_$DATE.sql
echo "✅ Бэкап создан: $BACKUP_DIR/familyway_backup_$DATE.sql.gz"
EOF

# Скрипт восстановления
cat > restore_database.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажите файл бэкапа"
    echo "Использование: ./restore_database.sh backup_file.sql.gz"
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="baybyway_production"
DB_USER="user_bayby1"
DB_PASSWORD="J@nym9494!"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Ошибка: Файл бэкапа не найден: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Восстановление базы данных из $BACKUP_FILE..."

if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME
else
    mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < $BACKUP_FILE
fi

echo "✅ База данных восстановлена успешно!"
EOF

# Делаем скрипты исполняемыми
chmod +x start_server.sh start_production.sh backup_database.sh restore_database.sh

# 9. Тестирование
echo "🧪 Шаг 9: Тестирование..."

# Проверка подключения к базе данных
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    print('✅ Подключение к MySQL: успешно')
"

# Проверка миграций
python manage.py showmigrations

# 10. Создание systemd сервиса
echo "🔧 Шаг 10: Создание systemd сервиса..."

cat > /etc/systemd/system/familyway.service << EOF
[Unit]
Description=FamilyWay + Django Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment=ENVIRONMENT=production
Environment=DJANGO_SETTINGS_MODULE=baybyway.settings
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --bind unix:$PROJECT_DIR/familyway.sock baybyway.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
systemctl daemon-reload

# 11. Финальная проверка
echo "📊 Шаг 11: Финальная проверка..."

echo "📊 Статус MySQL:"
systemctl status mysql --no-pager

echo "📊 Статус проекта:"
cd $PROJECT_DIR
source venv/bin/activate
python manage.py check

echo "📊 Информация о базе данных:"
mysql -u $DB_USER -p$DB_PASSWORD -e "SELECT 'Подключение успешно!' as status;"

echo ""
echo "✅ Настройка FamilyWay + с MySQL завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите сервер разработки: ./start_server.sh"
echo "2. Запустите продакшн сервер: ./start_production.sh"
echo "3. Создайте бэкап: ./backup_database.sh"
echo "4. Настройте Nginx для продакшена"
echo ""
echo "🔧 Полезные команды:"
echo "   Запуск сервера: ./start_server.sh"
echo "   Запуск продакшена: ./start_production.sh"
echo "   Бэкап БД: ./backup_database.sh"
echo "   Восстановление: ./restore_database.sh backup_file.sql.gz"
echo "   Подключение к MySQL: mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME"
echo "   Логи MySQL: tail -f /var/log/mysql/error.log"
echo ""
echo "🎉 FamilyWay + готов к работе с MySQL!"
