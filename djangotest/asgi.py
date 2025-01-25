import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Importer les URLs WebSocket de manière sûre
from djangoapp.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangotest.settings')

# Initialisation de Django
django_asgi_app = get_asgi_application()

# Configuration de l'application ASGI avec Channels
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Traite les requêtes HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
