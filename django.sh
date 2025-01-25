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
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin} \
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com} \
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-golemian123} \
python3 manage.py createsuperuser --noinput || true
echo ====================================

echo "Starting Server..."
python3 manage.py runserver 0.0.0.0:8000