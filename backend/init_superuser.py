import os
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from dotenv import load_dotenv

def init_superuser():
    load_dotenv()  # Charger les variables d'environnement
    
    DJANGO_SUPERUSER_USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME')
    DJANGO_SUPERUSER_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL')
    DJANGO_SUPERUSER_PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    
    User = get_user_model()
    if not User.objects.filter(username=DJANGO_SUPERUSER_USERNAME).exists():
        User.objects.create_superuser(
            username=DJANGO_SUPERUSER_USERNAME,
            email=DJANGO_SUPERUSER_EMAIL,
            password=DJANGO_SUPERUSER_PASSWORD
        )
        print('Superuser created successfully!')
    else:
        print('Superuser already exists.')
