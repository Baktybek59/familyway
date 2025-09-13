#!/usr/bin/env python3
"""
Test script for production settings.
"""

import os
import sys
import django
from django.conf import settings

def test_production_settings():
    """Test production settings."""
    print("🧪 Testing production settings...")
    print("=" * 50)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings_production')
    
    try:
        django.setup()
        print("✅ Django settings loaded successfully")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
                
        # Test static files configuration
        static_root = settings.STATIC_ROOT
        if os.path.exists(static_root) or os.path.isdir(os.path.dirname(static_root)):
            print("✅ Static files configuration valid")
        else:
            print("⚠️  Static files directory not found (will be created)")
            
        # Test media files configuration
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root) or os.path.isdir(os.path.dirname(media_root)):
            print("✅ Media files configuration valid")
        else:
            print("⚠️  Media files directory not found (will be created)")
            
        # Test security settings
        if not settings.DEBUG:
            print("✅ Debug mode disabled for production")
        else:
            print("❌ Debug mode is enabled (should be False in production)")
            
        # Test allowed hosts
        if '0.0.0.0' in settings.ALLOWED_HOSTS:
            print("✅ Allowed hosts configured")
        else:
            print("⚠️  Allowed hosts may need configuration")
            
        print("=" * 50)
        print("🎉 Production settings test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing production settings: {e}")
        return False

if __name__ == "__main__":
    success = test_production_settings()
    sys.exit(0 if success else 1)


