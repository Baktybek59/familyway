#!/bin/bash

# BaybyWay Production Startup Script
# This script starts the production server with all necessary configurations

echo "🚀 Starting BaybyWay Production Server..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if MySQL is running
echo "🔄 Checking MySQL connection..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baybyway.settings_production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ MySQL connection successful')
except Exception as e:
    print(f'❌ MySQL connection failed: {e}')
    print('Please check MySQL setup and run: python setup_mysql_simple.py')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --settings=baybyway.settings_production

# Collect static files
echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput --settings=baybyway.settings_production

# Compile translations
echo "🔄 Compiling translations..."
python manage.py compilemessages --settings=baybyway.settings_production

# Start server
echo "🚀 Starting production server..."
echo "Server will be available at: http://0.0.0.0:8000"
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Start with Gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 baybyway.wsgi_production:application


