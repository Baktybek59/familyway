#!/usr/bin/env python3
"""
Script to setup MySQL database for BaybyWay production.
Run this script to create database and user.
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database_and_user():
    """Create database and user for BaybyWay production."""
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',  # MySQL root user
        'password': input("Enter MySQL root password: "),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # Database and user details
    database_name = 'baybyway_production'
    username = 'baybyway_user'
    password = 'J@nym9494!'
    
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("✅ Connected to MySQL server")
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database_name}' created successfully")
        
        # Create user
        cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{password}'")
        print(f"✅ User '{username}' created successfully")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print(f"✅ Privileges granted to user '{username}'")
        
        # Test connection with new user
        test_connection = mysql.connector.connect(
            host='localhost',
            user=username,
            password=password,
            database=database_name
        )
        test_cursor = test_connection.cursor()
        test_cursor.execute("SELECT 1")
        print("✅ Test connection successful")
        
        test_cursor.close()
        test_connection.close()
        
    except Error as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ MySQL connection closed")

if __name__ == "__main__":
    print("🚀 Setting up MySQL database for BaybyWay production...")
    print("=" * 50)
    create_database_and_user()
    print("=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run migrations: python manage.py migrate --settings=baybyway.settings_production")
    print("3. Create superuser: python manage.py createsuperuser --settings=baybyway.settings_production")
    print("4. Collect static files: python manage.py collectstatic --settings=baybyway.settings_production")


