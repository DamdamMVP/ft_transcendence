import os
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

def init_superuser():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='golemian123'
        )
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
