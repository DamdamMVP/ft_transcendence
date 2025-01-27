from django.core.management.base import BaseCommand
from init_google_auth import init_google_auth

class Command(BaseCommand):
    help = 'Configure Google OAuth authentication settings'

    def handle(self, *args, **options):
        init_google_auth()
