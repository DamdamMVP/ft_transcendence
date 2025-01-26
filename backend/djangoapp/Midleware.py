from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import decode as jwt_decode, ExpiredSignatureError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.deprecation import MiddlewareMixin


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Get access token from cookies
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        # Validate the token
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            return None


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





User = get_user_model()

class TokenAuthMiddlewareHTTP(MiddlewareMixin):
    """
    Middleware pour gérer l'authentification par JWT dans les cookies HTTP.
    Si le token d'accès est expiré, utilise le token de rafraîchissement pour en générer un nouveau.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token:
            request.user = AnonymousUser()
            return

        try:
            # 1) Tenter de décoder le token d'accès
            decoded_data = jwt_decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            if not user_id:
                request.user = AnonymousUser()
                return
            
            # Récupérer l'utilisateur associé
            request.user = User.objects.get(id=user_id)

        except ExpiredSignatureError:
            # 2) Si le token d'accès est expiré, tenter de rafraîchir
            if not refresh_token:
                request.user = AnonymousUser()
                return

            try:
                # Rafraîchir le token
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)

                # Ajouter le nouveau token d'accès dans la réponse (cookies)
                request.new_access_token = new_access_token

                # Décoder le nouveau token
                new_decoded_data = jwt_decode(new_access_token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = new_decoded_data.get("user_id")
                if not user_id:
                    request.user = AnonymousUser()
                    return

                # Récupérer l'utilisateur
                request.user = User.objects.get(id=user_id)

            except InvalidToken:
                request.user = AnonymousUser()
                return

        except (InvalidToken, User.DoesNotExist):
            request.user = AnonymousUser()

    def process_response(self, request, response):
        # Si un nouveau token d'accès a été généré, le placer dans les cookies
        if hasattr(request, "new_access_token"):
            response.set_cookie(
                key="access_token",
                value=request.new_access_token,
                httponly=True,
                secure=settings.DEBUG is False,  # Utilisez HTTPS en production
                samesite="Lax",
            )
        return response