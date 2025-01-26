import os
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def init_google_auth():
    # Configure le site par défaut
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'ft_transcendence'
        }
    )
    if not created:
        site.domain = 'localhost:8000'
        site.name = 'ft_transcendence'
        site.save()

    # Récupère les identifiants Google des variables d'environnement
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    secret = os.getenv('GOOGLE_SECRET_KEY')

    if not client_id or not secret:
        print('Warning: GOOGLE_CLIENT_ID or GOOGLE_SECRET_KEY not set in environment variables')
        return

    # Configure l'application Google
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        name='Google OAuth',
        defaults={
            'client_id': client_id,
            'secret': secret,
        }
    )
    
    if not created:
        google_app.client_id = client_id
        google_app.secret = secret
        google_app.save()

    # Associe l'application au site
    google_app.sites.add(site)
    
    print('Google authentication configured successfully!')
