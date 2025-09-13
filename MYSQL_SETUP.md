# MySQL Setup для BaybyWay

## 🗄️ Настройка базы данных

### 1. Установка MySQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server mysql-client libmysqlclient-dev

# CentOS/RHEL
sudo yum install mysql-server mysql-devel

# Запуск MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2. Настройка MySQL

```bash
# Безопасная настройка MySQL
sudo mysql_secure_installation
```

### 3. Создание базы данных и пользователя

#### Вариант 1: Автоматический (рекомендуется)
```bash
python setup_mysql.py
```

#### Вариант 2: Ручной
```sql
-- Подключение к MySQL как root
mysql -u root -p

-- Создание базы данных
CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создание пользователя
CREATE USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';

-- Предоставление прав
GRANT ALL PRIVILEGES ON baybyway_production.* TO 'baybyway_user'@'localhost';
FLUSH PRIVILEGES;

-- Выход
EXIT;
```

### 4. Проверка подключения

```bash
# Тест подключения
mysql -u baybyway_user -p baybyway_production

# В MySQL консоли
SHOW DATABASES;
USE baybyway_production;
SHOW TABLES;
```

## 🔧 Конфигурация

### Параметры подключения:
- **Хост**: `localhost`
- **Порт**: `3306`
- **База данных**: `baybyway_production`
- **Пользователь**: `baybyway_user`
- **Пароль**: `J@nym9494!`
- **Кодировка**: `utf8mb4`

### Файл конфигурации MySQL (`/etc/mysql/mysql.conf.d/mysqld.cnf`):

```ini
[mysqld]
# Основные настройки
bind-address = 127.0.0.1
port = 3306

# Кодировка
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Производительность
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
max_connections = 100

# Логирование
log-error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

## 🚀 Запуск миграций

```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск миграций
python manage.py migrate --settings=baybyway.settings_production

# Создание суперпользователя
python manage.py createsuperuser --settings=baybyway.settings_production

# Сбор статических файлов
python manage.py collectstatic --noinput --settings=baybyway.settings_production
```

## 🔒 Безопасность

### 1. Ограничение доступа
```sql
-- Удаление анонимных пользователей
DELETE FROM mysql.user WHERE User='';

-- Удаление тестовой базы данных
DROP DATABASE IF EXISTS test;

-- Перезагрузка привилегий
FLUSH PRIVILEGES;
```

### 2. Настройка файрвола
```bash
# Ubuntu/Debian
sudo ufw allow from 127.0.0.1 to any port 3306
sudo ufw deny 3306

# CentOS/RHEL
sudo firewall-cmd --permanent --add-rich-rule="rule family='ipv4' source address='127.0.0.1' port protocol='tcp' port='3306' accept"
sudo firewall-cmd --reload
```

### 3. Резервное копирование
```bash
# Создание бэкапа
mysqldump -u baybyway_user -p baybyway_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
mysql -u baybyway_user -p baybyway_production < backup_file.sql
```

## 🆘 Устранение неполадок

### Проблема: "Access denied for user"
```bash
# Сброс пароля
sudo mysql -u root
ALTER USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';
FLUSH PRIVILEGES;
```

### Проблема: "Can't connect to MySQL server"
```bash
# Проверка статуса
sudo systemctl status mysql

# Перезапуск
sudo systemctl restart mysql

# Проверка портов
sudo netstat -tlnp | grep 3306
```

### Проблема: "Unknown database"
```sql
-- Создание базы данных
CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📊 Мониторинг

### Проверка подключений
```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Connections';
```

### Проверка производительности
```sql
SHOW STATUS LIKE 'Slow_queries';
SHOW STATUS LIKE 'Uptime';
```

### Логи
```bash
# Ошибки MySQL
sudo tail -f /var/log/mysql/error.log

# Медленные запросы
sudo tail -f /var/log/mysql/slow.log
```


