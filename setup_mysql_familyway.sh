#!/bin/bash

# Скрипт для настройки MySQL для FamilyWay +
# Использование: sudo ./setup_mysql_familyway.sh

set -e

echo "🗄️  Настройка MySQL для FamilyWay +"
echo "=================================="

# Переменные
DB_NAME="baybyway_production"
DB_USER="user_bayby1"
DB_PASSWORD="J@nym9494!"
DB_HOST="localhost"
DB_PORT="3306"

# Проверка прав администратора
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: Запустите скрипт с правами администратора (sudo)"
    exit 1
fi

echo "📋 Информация о базе данных:"
echo "   Имя базы: $DB_NAME"
echo "   Пользователь: $DB_USER"
echo "   Хост: $DB_HOST"
echo "   Порт: $DB_PORT"
echo ""

# Обновление системы
echo "🔄 Обновление системы..."
apt update && apt upgrade -y

# Установка MySQL Server
echo "📦 Установка MySQL Server..."
apt install -y mysql-server mysql-client

# Запуск и включение MySQL
echo "🚀 Запуск MySQL..."
systemctl start mysql
systemctl enable mysql

# Проверка статуса MySQL
echo "📊 Проверка статуса MySQL..."
systemctl status mysql --no-pager

# Настройка MySQL
echo "⚙️  Настройка MySQL..."

# Создание скрипта настройки MySQL
cat > /tmp/mysql_setup.sql << EOF
-- Создание базы данных
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создание пользователя
CREATE USER IF NOT EXISTS '$DB_USER'@'$DB_HOST' IDENTIFIED BY '$DB_PASSWORD';

-- Предоставление прав
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'$DB_HOST';

-- Обновление прав
FLUSH PRIVILEGES;

-- Показать созданные базы данных
SHOW DATABASES;

-- Показать пользователей
SELECT User, Host FROM mysql.user WHERE User = '$DB_USER';
EOF

# Выполнение скрипта настройки
echo "🔧 Выполнение настройки базы данных..."
mysql -u root -e "source /tmp/mysql_setup.sql"

# Удаление временного файла
rm /tmp/mysql_setup.sql

# Установка Python MySQL клиента
echo "🐍 Установка Python MySQL клиента..."
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

# Установка MySQL connector для Python
pip3 install mysqlclient

# Проверка подключения к базе данных
echo "🔍 Проверка подключения к базе данных..."
python3 -c "
import MySQLdb
try:
    conn = MySQLdb.connect(
        host='$DB_HOST',
        port=$DB_PORT,
        user='$DB_USER',
        passwd='$DB_PASSWORD',
        db='$DB_NAME',
        charset='utf8mb4'
    )
    print('✅ Подключение к MySQL успешно!')
    conn.close()
except Exception as e:
    print(f'❌ Ошибка подключения к MySQL: {e}')
    exit(1)
"

# Настройка безопасности MySQL
echo "🔒 Настройка безопасности MySQL..."
mysql_secure_installation << EOF
n
y
y
y
y
EOF

# Создание конфигурационного файла MySQL
echo "📝 Создание конфигурационного файла MySQL..."
cat > /etc/mysql/mysql.conf.d/familyway.cnf << EOF
[mysqld]
# Основные настройки
default-storage-engine = InnoDB
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Настройки производительности
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Настройки безопасности
local-infile = 0
symbolic-links = 0

# Настройки подключения
max_connections = 100
max_connect_errors = 1000
wait_timeout = 600
interactive_timeout = 600

# Логирование
log-error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# Настройки для Django
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO
EOF

# Перезапуск MySQL с новой конфигурацией
echo "🔄 Перезапуск MySQL с новой конфигурацией..."
systemctl restart mysql

# Проверка конфигурации
echo "🔍 Проверка конфигурации MySQL..."
mysql -u root -e "SHOW VARIABLES LIKE 'character_set%';"
mysql -u root -e "SHOW VARIABLES LIKE 'collation%';"

# Создание скрипта для миграций Django
echo "📝 Создание скрипта для миграций Django..."
cat > migrate_to_mysql.sh << 'EOF'
#!/bin/bash

echo "🔄 Выполнение миграций Django на MySQL..."

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install mysqlclient

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя (если нужно)
echo "👤 Создание суперпользователя..."
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic --noinput

echo "✅ Миграции завершены успешно!"
EOF

chmod +x migrate_to_mysql.sh

# Создание скрипта для бэкапа
echo "💾 Создание скрипта для бэкапа..."
cat > backup_mysql.sh << 'EOF'
#!/bin/bash

# Скрипт для бэкапа MySQL базы данных FamilyWay +

DB_NAME="baybyway_production"
DB_USER="user_bayby1"
DB_PASSWORD="J@nym9494!"
BACKUP_DIR="/home/gurusan/Документы/baybyWay/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Создание бэкапа
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/familyway_backup_$DATE.sql

# Сжатие бэкапа
gzip $BACKUP_DIR/familyway_backup_$DATE.sql

echo "✅ Бэкап создан: $BACKUP_DIR/familyway_backup_$DATE.sql.gz"
EOF

chmod +x backup_mysql.sh

# Создание скрипта для восстановления
echo "🔄 Создание скрипта для восстановления..."
cat > restore_mysql.sh << 'EOF'
#!/bin/bash

# Скрипт для восстановления MySQL базы данных FamilyWay +

if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажите файл бэкапа"
    echo "Использование: ./restore_mysql.sh backup_file.sql.gz"
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

# Распаковка (если сжат)
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME
else
    mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < $BACKUP_FILE
fi

echo "✅ База данных восстановлена успешно!"
EOF

chmod +x restore_mysql.sh

# Финальная проверка
echo "🧪 Финальная проверка..."
echo "📊 Статус MySQL:"
systemctl status mysql --no-pager

echo "📊 Подключение к базе данных:"
mysql -u $DB_USER -p$DB_PASSWORD -e "SELECT 'Подключение успешно!' as status;"

echo "📊 Информация о базе данных:"
mysql -u $DB_USER -p$DB_PASSWORD -e "SHOW DATABASES;"

echo ""
echo "✅ Настройка MySQL завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите миграции: ./migrate_to_mysql.sh"
echo "2. Запустите сервер: python manage.py runserver"
echo "3. Создайте бэкап: ./backup_mysql.sh"
echo ""
echo "🔧 Полезные команды:"
echo "   Подключение к MySQL: mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME"
echo "   Статус MySQL: systemctl status mysql"
echo "   Логи MySQL: tail -f /var/log/mysql/error.log"
echo "   Бэкап: ./backup_mysql.sh"
echo "   Восстановление: ./restore_mysql.sh backup_file.sql.gz"
echo ""
echo "🎉 FamilyWay + готов к работе с MySQL!"
