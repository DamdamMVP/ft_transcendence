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
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import jwt
from datetime import datetime, timezone

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Get access token from cookies
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                payload = jwt.decode(
                    access_token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                print('jai trouve un token')
                exp = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
                if exp > datetime.now(timezone.utc):
                    print("token not expired")
                    validated_token = self.get_validated_token(access_token)
                    user = self.get_user(validated_token)
                    return (user, validated_token)
            except:
                print("token expired")
                pass
        
        print("acces token not found or not valid, supposed to call the refresh")
        refresh_token = request.COOKIES.get('refresh_token')
        refresh = RefreshToken(refresh_token)
            # Generate a new access token
        access_token = str(refresh.access_token)
        response = JsonResponse({'status': 'token refreshed'})
        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=3600 * 24,
            httponly=True,
            secure=True,
            samesite='None'
        )
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            print("Authentication success midleware after trying to refresh")
            return (user, validated_token)
        except AuthenticationFailed:
            print("Authentication failed midleware after trying to refresh")
            return None


class CookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        custom_response = getattr(request, '_custom_response', None)
        if custom_response:
            response.set_cookie(
                key=custom_response['cookie_name'],
                value=custom_response['cookie_value'],
                max_age=custom_response['max_age'],
                httponly=custom_response['httponly'],
                secure=custom_response['secure'],
                samesite=custom_response['samesite']
            )
        print("cookie middleware")
        return response


User = get_user_model()


from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import ExpiredSignatureError, decode as jwt_decode
from django.conf import settings

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
        # Parse cookies from the headers
        headers = dict(scope["headers"])
        cookie_header = headers.get(b"cookie", b"").decode()

        cookies = {}
        for item in cookie_header.split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()

        access_token = cookies.get("access_token")
        refresh_token = cookies.get("refresh_token")

        # Attempt to authenticate user (and possibly refresh tokens)
        user, access_token = await self.get_user_from_tokens(access_token, refresh_token)

        scope["user"] = user
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_tokens(self, access_token, refresh_token):
        """
        Checks if the access token is valid. If expired, tries to refresh using the
        refresh token. Returns (user, new_access_token).
        new_access_token is None if we didn't refresh.
        """
        if not access_token:
            return AnonymousUser(), None

        try:
            # Try decoding the current access token
            decoded_data = jwt_decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            if not user_id:
                return AnonymousUser(), None

            #Get the user from DB
            user = User.objects.get(id=user_id)
            return user, None

        except ExpiredSignatureError:
            # If the access token is expired, attempt to refresh
            if not refresh_token:
                return AnonymousUser(), None

            try:
                refresh = RefreshToken(refresh_token)

                new_access_token = str(refresh.access_token)
                
                new_decoded_data = jwt_decode(
                    new_access_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = new_decoded_data.get("user_id")
                if not user_id:
                    return AnonymousUser(), None

                user = User.objects.get(id=user_id)
                return user, new_access_token

            except Exception:
                # If refresh fails return anonymous
                return AnonymousUser(), None

        except (InvalidToken, User.DoesNotExist):
            return AnonymousUser(), None
