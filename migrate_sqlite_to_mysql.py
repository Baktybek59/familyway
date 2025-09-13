#!/usr/bin/env python3
"""
Скрипт для миграции данных с SQLite на MySQL для FamilyWay +
Использование: python migrate_sqlite_to_mysql.py
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings')
django.setup()

from django.db import connections
from django.core.management import execute_from_command_line
import json

def check_sqlite_file():
    """Проверяет наличие SQLite файла"""
    sqlite_path = BASE_DIR / 'db.sqlite3'
    if not sqlite_path.exists():
        print("❌ SQLite файл не найден: db.sqlite3")
        return False
    print(f"✅ SQLite файл найден: {sqlite_path}")
    return True

def check_mysql_connection():
    """Проверяет подключение к MySQL"""
    try:
        # Временно переключаемся на SQLite для проверки
        from django.conf import settings
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
        settings.DATABASES['default']['NAME'] = BASE_DIR / 'db.sqlite3'
        
        # Проверяем SQLite
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"✅ SQLite подключение: найдено {len(tables)} таблиц")
        
        # Переключаемся на MySQL
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
        settings.DATABASES['default']['NAME'] = 'baybyway_production'
        settings.DATABASES['default']['USER'] = 'user_bayby1'
        settings.DATABASES['default']['PASSWORD'] = 'J@nym9494!'
        settings.DATABASES['default']['HOST'] = 'localhost'
        settings.DATABASES['default']['PORT'] = '3306'
        settings.DATABASES['default']['OPTIONS'] = {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
        
        # Проверяем MySQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ MySQL подключение: успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к MySQL: {e}")
        return False

def export_sqlite_data():
    """Экспортирует данные из SQLite"""
    print("📤 Экспорт данных из SQLite...")
    
    try:
        # Переключаемся на SQLite
        from django.conf import settings
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
        settings.DATABASES['default']['NAME'] = BASE_DIR / 'db.sqlite3'
        
        from django.db import connection
        with connection.cursor() as cursor:
            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'django_%';")
            tables = [row[0] for row in cursor.fetchall()]
            
            exported_data = {}
            
            for table in tables:
                print(f"  📋 Экспорт таблицы: {table}")
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Получаем названия колонок
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                exported_data[table] = {
                    'columns': columns,
                    'rows': rows
                }
            
            # Сохраняем данные в JSON
            with open('sqlite_export.json', 'w', encoding='utf-8') as f:
                json.dump(exported_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Экспорт завершен: {len(tables)} таблиц сохранено в sqlite_export.json")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка экспорта: {e}")
        return False

def run_django_migrations():
    """Запускает миграции Django"""
    print("🔄 Запуск миграций Django...")
    
    try:
        # Переключаемся на MySQL
        from django.conf import settings
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
        settings.DATABASES['default']['NAME'] = 'baybyway_production'
        settings.DATABASES['default']['USER'] = 'user_bayby1'
        settings.DATABASES['default']['PASSWORD'] = 'J@nym9494!'
        settings.DATABASES['default']['HOST'] = 'localhost'
        settings.DATABASES['default']['PORT'] = '3306'
        settings.DATABASES['default']['OPTIONS'] = {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
        
        # Запускаем миграции
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Миграции Django выполнены успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграций: {e}")
        return False

def import_data_to_mysql():
    """Импортирует данные в MySQL"""
    print("📥 Импорт данных в MySQL...")
    
    try:
        # Загружаем экспортированные данные
        with open('sqlite_export.json', 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        # Переключаемся на MySQL
        from django.conf import settings
        settings.DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
        settings.DATABASES['default']['NAME'] = 'baybyway_production'
        settings.DATABASES['default']['USER'] = 'user_bayby1'
        settings.DATABASES['default']['PASSWORD'] = 'J@nym9494!'
        settings.DATABASES['default']['HOST'] = 'localhost'
        settings.DATABASES['default']['PORT'] = '3306'
        settings.DATABASES['default']['OPTIONS'] = {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
        
        from django.db import connection
        with connection.cursor() as cursor:
            for table_name, table_data in exported_data.items():
                print(f"  📋 Импорт таблицы: {table_name}")
                
                columns = table_data['columns']
                rows = table_data['rows']
                
                if not rows:
                    print(f"    ⚠️  Таблица {table_name} пуста, пропускаем")
                    continue
                
                # Создаем SQL для вставки
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join(columns)
                insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                try:
                    cursor.executemany(insert_sql, rows)
                    print(f"    ✅ Импортировано {len(rows)} записей")
                except Exception as e:
                    print(f"    ⚠️  Ошибка импорта таблицы {table_name}: {e}")
                    continue
        
        print("✅ Импорт данных завершен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def cleanup_files():
    """Очищает временные файлы"""
    print("🧹 Очистка временных файлов...")
    
    files_to_remove = ['sqlite_export.json']
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  🗑️  Удален: {file_path}")

def main():
    """Основная функция"""
    print("🔄 Миграция с SQLite на MySQL для FamilyWay +")
    print("=" * 50)
    
    # Проверки
    if not check_sqlite_file():
        return False
    
    if not check_mysql_connection():
        return False
    
    # Экспорт данных
    if not export_sqlite_data():
        return False
    
    # Миграции Django
    if not run_django_migrations():
        return False
    
    # Импорт данных
    if not import_data_to_mysql():
        return False
    
    # Очистка
    cleanup_files()
    
    print("")
    print("✅ Миграция завершена успешно!")
    print("")
    print("📋 Следующие шаги:")
    print("1. Проверьте работу сайта: python manage.py runserver")
    print("2. Создайте суперпользователя: python manage.py createsuperuser")
    print("3. Соберите статические файлы: python manage.py collectstatic")
    print("")
    print("🎉 FamilyWay + теперь работает с MySQL!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
