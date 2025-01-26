from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
<<<<<<< HEAD
from jwt import decode as jwt_decode, ExpiredSignatureError
=======
>>>>>>> c35a75964efecd843b638411b877eb5299c3f688
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

<<<<<<< HEAD
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import decode as jwt_decode, ExpiredSignatureError

User = get_user_model()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom Channels middleware that:
    1) Reads 'access_token' and 'refresh_token' cookies.
    2) Tries to decode the access token.
    3) If expired, uses the refresh token to get a new access token.
    4) Decodes the new access token to get the user.
    5) Attaches user to scope as scope['user'].
    """

    async def __call__(self, scope, receive, send):
        # Parse cookies from the headers in scope
        headers = dict(scope["headers"])
        cookie_header = headers.get(b"cookie", b"").decode()

        cookies = {}
        for item in cookie_header.split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()

        access_token = cookies.get("access_token")
        refresh_token = cookies.get("refresh_token")

        # Attempt to authenticate user
        user = await self.get_user_from_tokens(access_token, refresh_token)
        scope["user"] = user

        # Continue the handshake/connection
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_tokens(self, access_token, refresh_token):
        if not access_token:
            return AnonymousUser()

        try:
            # 1) Try decoding the current access token
            decoded_data = jwt_decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            if not user_id:
                return AnonymousUser()
            return User.objects.get(id=user_id)

        except ExpiredSignatureError:
            # 2) If the access token is expired, attempt to refresh
            if not refresh_token:
                return AnonymousUser()

            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                
                # Decode the newly generated access token
                new_decoded_data = jwt_decode(new_access_token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = new_decoded_data.get("user_id")
                if not user_id:
                    return AnonymousUser()
                
                return User.objects.get(id=user_id)

            except Exception:
                # If refresh fails (invalid/expired refresh token), anonymous
                return AnonymousUser()

        except (InvalidToken, User.DoesNotExist):
            return AnonymousUser()
=======
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
>>>>>>> c35a75964efecd843b638411b877eb5299c3f688
