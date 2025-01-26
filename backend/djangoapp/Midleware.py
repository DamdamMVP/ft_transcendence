from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Récupère le token d'accès depuis les cookies
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        # Valide le token
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            return None


User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get("user_id")
        if not user_id:
            return AnonymousUser()
        return User.objects.get(id=user_id)
    except (InvalidToken, User.DoesNotExist):
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extraire le cookie 'access_token'
        headers = dict(scope['headers'])
        cookie_header = headers.get(b'cookie', b'').decode()
        cookies = {key.strip(): value.strip() for key, value in (item.split('=') for item in cookie_header.split(';') if '=' in item)}
        token = cookies.get('access_token')

        # Vérifier le token et récupérer l'utilisateur
        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()

        # Continuer vers le consumer
        return await super().__call__(scope, receive, send)
