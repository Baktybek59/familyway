#!/usr/bin/env python3
"""
Deployment script for BaybyWay production.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function."""
    print("🚀 Starting BaybyWay production deployment...")
    print("=" * 60)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings_production')
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run migrations
    if not run_command("python manage.py migrate --settings=baybyway.settings_production", "Running database migrations"):
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput --settings=baybyway.settings_production", "Collecting static files"):
        sys.exit(1)
    
    # Compile translations
    if not run_command("python manage.py compilemessages --settings=baybyway.settings_production", "Compiling translations"):
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 Deployment completed successfully!")
    print("\nTo start the production server:")
    print("gunicorn --bind 0.0.0.0:8000 baybyway.wsgi:application")
    print("\nOr with more workers:")
    print("gunicorn --workers 3 --bind 0.0.0.0:8000 baybyway.wsgi:application")

if __name__ == "__main__":
    main()


