# Ручная настройка MySQL для BaybyWay

## 🗄️ Пошаговая инструкция

### 1. Подключение к MySQL

```bash
# Подключение как root
sudo mysql -u root -p
```

### 2. Создание базы данных

```sql
-- Создание базы данных
CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Проверка создания
SHOW DATABASES;
```

### 3. Создание пользователя

```sql
-- Создание пользователя
CREATE USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';

-- Проверка создания
SELECT User, Host FROM mysql.user WHERE User = 'baybyway_user';
```

### 4. Предоставление прав

```sql
-- Предоставление всех прав на базу данных
GRANT ALL PRIVILEGES ON baybyway_production.* TO 'baybyway_user'@'localhost';

-- Применение изменений
FLUSH PRIVILEGES;

-- Проверка прав
SHOW GRANTS FOR 'baybyway_user'@'localhost';
```

### 5. Тест подключения

```sql
-- Выход из MySQL
EXIT;
```

```bash
# Тест подключения с новым пользователем
mysql -u baybyway_user -p baybyway_production

# В MySQL консоли
SHOW TABLES;
EXIT;
```

### 6. Запуск Django

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

### 7. Тест приложения

```bash
# Запуск тестового сервера
python manage.py runserver --settings=baybyway.settings_production

# Или с Gunicorn
gunicorn --bind 0.0.0.0:8000 baybyway.wsgi_production:application
```

## 🔧 Альтернативные команды

### Если MySQL требует аутентификацию через unix_socket:

```bash
# Подключение без пароля
sudo mysql

# Создание пользователя с аутентификацией через mysql_native_password
CREATE USER 'baybyway_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'J@nym9494!';
GRANT ALL PRIVILEGES ON baybyway_production.* TO 'baybyway_user'@'localhost';
FLUSH PRIVILEGES;
```

### Если нужно изменить пароль:

```sql
-- Изменение пароля
ALTER USER 'baybyway_user'@'localhost' IDENTIFIED BY 'J@nym9494!';
FLUSH PRIVILEGES;
```

## 🆘 Устранение неполадок

### Ошибка: "Access denied for user 'baybyway_user'@'localhost'"

```sql
-- Проверка пользователя
SELECT User, Host, plugin FROM mysql.user WHERE User = 'baybyway_user';

-- Если plugin = 'auth_socket', измените на mysql_native_password
ALTER USER 'baybyway_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'J@nym9494!';
FLUSH PRIVILEGES;
```

### Ошибка: "Unknown database 'baybyway_production'"

```sql
-- Создание базы данных
CREATE DATABASE baybyway_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Ошибка: "Table doesn't exist"

```bash
# Запуск миграций
python manage.py migrate --settings=baybyway.settings_production
```

## ✅ Проверка успешной настройки

После выполнения всех шагов вы должны увидеть:

1. ✅ База данных `baybyway_production` создана
2. ✅ Пользователь `baybyway_user` создан
3. ✅ Права предоставлены
4. ✅ Django подключается к базе данных
5. ✅ Миграции выполнены
6. ✅ Приложение запускается

## 🚀 Следующие шаги

После успешной настройки MySQL:

1. **Запустите приложение**: `gunicorn --bind 0.0.0.0:8000 baybyway.wsgi_production:application`
2. **Настройте nginx** (опционально)
3. **Настройте systemd сервис** (опционально)
4. **Настройте SSL сертификаты** (опционально)


