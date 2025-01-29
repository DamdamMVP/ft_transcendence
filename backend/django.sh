#!/bin/bash


echo "Waiting for PostgreSQL to be ready..."
/wait-for-it.sh $PG_HOST:$PG_PORT --timeout=30 --strict -- echo "PostgreSQL is ready!"


echo "Creating Migrations..."
python3 manage.py makemigrations djangoapp
echo ====================================

echo "Starting Migrations..."
python3 manage.py migrate
echo ====================================

echo "Creating Superuser if needed..."
if [ -z "$DJANGO_SUPERUSER_USERNAME" ] || [ -z "$DJANGO_SUPERUSER_EMAIL" ] || [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Error: Missing required environment variables for superuser creation"
    echo "Please make sure DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD are set in your .env file"
    exit 1
fi
python3 manage.py createsuperuser --noinput || true
echo ====================================

echo "Starting Server..."
python3 manage.py runserver 0.0.0.0:8000