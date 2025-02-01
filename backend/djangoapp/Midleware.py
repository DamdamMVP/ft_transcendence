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
            # Générer un nouveau access token
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

        # Attempt to authenticate user (and possibly refresh tokens)
        user, new_access_token = await self.get_user_from_tokens(access_token, refresh_token)

        # Attach user to the scope
        scope["user"] = user

        # NOTE: If you wanted to somehow send the new_access_token back to the client
        # during the handshake, you'd have to add some handshake header or a
        # custom protocol approach. Channels doesn't have a direct "set-cookie" concept
        # for WebSocket upgrades. You might do something like:
        #
        # if new_access_token:
        #     # Some advanced hack to modify an HTTP handshake response header
        #     # But there's no simple built-in for that in Channels
        #     pass

        # Continue with the connection
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
            # 1) Try decoding the current access token
            decoded_data = jwt_decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            if not user_id:
                return AnonymousUser(), None

            # 2) Fetch the user from DB
            user = User.objects.get(id=user_id)
            return user, None

        except ExpiredSignatureError:
            # The access token is expired, attempt to refresh
            if not refresh_token:
                return AnonymousUser(), None

            try:
                refresh = RefreshToken(refresh_token)
                # Generate new access token
                new_access_token = str(refresh.access_token)
                
                # Decode the newly generated access token
                new_decoded_data = jwt_decode(
                    new_access_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = new_decoded_data.get("user_id")
                if not user_id:
                    return AnonymousUser(), None

                user = User.objects.get(id=user_id)
                return user, new_access_token

            except Exception:
                # If refresh fails (invalid/expired refresh token), anonymous
                return AnonymousUser(), None

        except (InvalidToken, User.DoesNotExist):
            return AnonymousUser(), None





User = get_user_model()

class TokenAuthMiddlewareHTTP(MiddlewareMixin):
    """
    Middleware to handle JWT authentication in HTTP cookies.
    If the access token is expired, uses the refresh token to generate a new one.
    """

    def process_request(self, request):
        # Get tokens from cookies
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        # Default to anonymous user
        request.user = AnonymousUser()

        if not access_token:
            return None

        try:
            # Try to decode the current access token
            decoded_data = jwt_decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get("user_id")
            
            if user_id:
                try:
                    request.user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass

        except ExpiredSignatureError:
            # Access token expired, try refresh flow
            if refresh_token:
                try:
                    # Attempt to refresh the token
                    refresh = RefreshToken(refresh_token)
                    new_access_token = str(refresh.access_token)
                    
                    # Decode the new token
                    new_decoded_data = jwt_decode(
                        new_access_token, 
                        settings.SECRET_KEY, 
                        algorithms=["HS256"]
                    )
                    user_id = new_decoded_data.get("user_id")
                    
                    if user_id:
                        try:
                            request.user = User.objects.get(id=user_id)
                            # Store the new token to be set in response
                            request.new_access_token = new_access_token
                        except User.DoesNotExist:
                            pass
                            
                except (InvalidToken, Exception) as e:
                    # Log the error for debugging
                    print(f"Token refresh failed: {str(e)}")
                    pass

        except (InvalidToken, Exception) as e:
            # Log the error for debugging
            print(f"Token validation failed: {str(e)}")
            pass

        return None

    def process_response(self, request, response):
        # Set the new access token in cookies if it was refreshed
        if hasattr(request, 'new_access_token'):
            response.set_cookie(
                key='access_token',
                value=request.new_access_token,
                httponly=True,
                secure=not settings.DEBUG,  # True in production
                samesite='None',
                max_age=3600 * 24  # 15 minutes, matching ACCESS_TOKEN_LIFETIME
            )
        
        return response