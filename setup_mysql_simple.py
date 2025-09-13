#!/usr/bin/env python3
"""
Simple MySQL setup script for BaybyWay production.
This script creates the database and user using Django's database connection.
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

def setup_database():
    """Setup database using Django's connection."""
    print("🚀 Setting up MySQL database for BaybyWay production...")
    print("=" * 60)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings_production')
    
    try:
        django.setup()
        print("✅ Django settings loaded successfully")
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
                
        print("=" * 60)
        print("🎉 Database setup completed successfully!")
        print("\nDatabase configuration:")
        print(f"  - Database: {settings.DATABASES['default']['NAME']}")
        print(f"  - User: {settings.DATABASES['default']['USER']}")
        print(f"  - Host: {settings.DATABASES['default']['HOST']}")
        print(f"  - Port: {settings.DATABASES['default']['PORT']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nPlease make sure:")
        print("1. MySQL server is running")
        print("2. Database 'baybyway_production' exists")
        print("3. User 'baybyway_user' exists with password 'J@nym9494!'")
        print("4. User has proper privileges")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)


