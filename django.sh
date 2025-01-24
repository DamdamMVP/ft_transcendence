#!/bin/bash


echo "Waiting for PostgreSQL to be ready..."
/wait-for-it.sh $PG_HOST:$PG_PORT --timeout=30 --strict -- echo "PostgreSQL is ready!"


echo "Creating Migrations..."
python3 manage.py makemigrations djangoapp
echo ====================================

echo "Starting Migrations..."
python3 manage.py migrate
echo ====================================

echo "Starting Server..."
python3 manage.py runserver 0.0.0.0:8000