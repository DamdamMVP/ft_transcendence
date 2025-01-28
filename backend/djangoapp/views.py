from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import User, History, Block
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from rest_framework import status
<<<<<<< HEAD
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserStatus

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def online_users(request):
    online_users = UserStatus.objects.filter(is_online=True).values_list('user_id', flat=True)
    return Response(list(online_users), status=200)
=======
import requests
from django.conf import settings
from django.urls import reverse
>>>>>>> 6963568 (login 42 seems ok but no popup)

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserStatus

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def online_users(request):
    online_users = UserStatus.objects.filter(is_online=True).values("user__id", "user__username")
    return Response({"online_users": list(online_users)}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    user = authenticate(request, username=email, password=password)

    if user:
        # Mettre à jour le statut en ligne
        status, _ = UserStatus.objects.get_or_create(user=user)
        status.is_online = True
        status.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            'message': 'User authenticated',
            'user': UserSerializer(user).data,
        }, status=200)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='None',
            max_age=900 
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='None',
            max_age=60 * 60 * 24 * 7  # 7 jours
        )

        return response
    else:
        return Response({'error': 'Invalid email or password'}, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        return Response({'error': 'No refresh token provided'}, status=400)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)

        response = Response({
            'message': 'Access token refreshed successfully',
            'user_id': refresh['user_id']
        }, status=200)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=60 * 60 * 3  # 3 heures en secondes
        )
        return response
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=400)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    # Mettre à jour le statut en ligne
    user = request.user
    status, _ = UserStatus.objects.get_or_create(user=user)
    status.is_online = False
    status.save()

    response = Response({'message': 'Logged out successfully'}, status=200)

    # Delete cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response


# Get all users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getData(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# Get a specific user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# Add a new user (with password hashing)
@api_view(['POST'])
@permission_classes([AllowAny])  # Allows access without authentication
def addUser(request):
    data = request.data

    # Hash password
    password = data.get('password')

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    data['password'] = make_password(data['password'])
    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    try:
        # Check that the user making the request corresponds to the user to be updated
        if int(request.user.id) != int(pk):  # Ensure both are integers
            return Response({'error': 'You can only update your own account.'}, status=403)
        
        user = User.objects.get(id=pk)
        data = request.data

        # Only allow `username` and `email` fields to be updated
        allowed_fields = ['username', 'email']
        update_data = {field: data[field] for field in allowed_fields if field in data}

        # Check that allowed fields are present and valid
        if not update_data:
            return Response({'error': 'Only username and email can be updated.'}, status=400)

        serializer = UserSerializer(instance=user, data=update_data, partial=True)  # Use `partial=True` to only require provided fields
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)



# Delete a user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response({'message': 'User successfully deleted!'}, status=200)

# User login
@api_view(['GET'])
@permission_classes([AllowAny])
def connect(request):
    from django.shortcuts import redirect
    import os
    from urllib.parse import urlencode

    # Google OAuth2 parameters
    params = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'redirect_uri': 'http://localhost:8000/accounts/google/login/callback/',
        'scope': 'email profile',
        'response_type': 'code',
        'access_type': 'online',
        'service': 'lso',
        'o2v': '2',
        'flowName': 'GeneralOAuthFlow'
    }
    
    # Construct the Google OAuth URL
    base_url = 'https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount'
    oauth_url = f"{base_url}?{urlencode(params)}"
    
    return redirect(oauth_url)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateProfilePicture(request, pk):
    try:
        user = User.objects.get(id=pk)

        if 'profile_picture' not in request.FILES:
            return Response({'error': 'No profile picture provided'}, status=400)

        # Update profile picture
        user.profile_picture = request.FILES['profile_picture']
        user.save()

        return Response({'message': 'Profile picture updated successfully'}, status=200)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePassword(request, pk):
    try:
        user = User.objects.get(id=pk)
        data = request.data

        if not check_password(data['old_password'], user.password):
            return Response({'error': 'Invalid old password'}, status=400)

        password = data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        data['password'] = make_password(data['password'])
        serializer = UserSerializer(instance=user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password updated successfully'}, status=200)
        return Response(serializer.errors, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateTheme(request, pk):
    try:
        user = User.objects.get(id=pk)
        theme = request.data.get('theme')
        
        if theme not in ['dark', 'light', 'forest']:
            return Response({'error': 'Invalid theme'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.theme = theme
        user.save()
        
        return Response({
            'message': 'Theme updated successfully',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request, friend_id):
    try:
        user = request.user
        friend = User.objects.get(id=friend_id)
        
        if user == friend:
            return Response({'error': 'You cannot add yourself as a friend'}, status=status.HTTP_400_BAD_REQUEST)
        
        if friend in user.friends.all():
            return Response({'error': 'This user is already your friend'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.add(friend)
        return Response({'message': f'Successfully added {friend.username} as friend'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend(request, friend_id):
    try:
        user = request.user
        friend = User.objects.get(id=friend_id)
        
        if friend not in user.friends.all():
            return Response({'error': 'This user is not in your friend list'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.remove(friend)
        return Response({'message': f'Successfully removed {friend.username} from friends'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends(request):
    user = request.user
    friends = user.friends.all()
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request):
    blocker = request.user
    blocked_id = request.data.get("blocked_id")

    # Check if blocked user ID is provided
    if not blocked_id:
        return Response({"error": "Blocked user ID is required."}, status=400)

    try:
        # Check if user exists
        blocked = User.objects.get(id=blocked_id)

        # Prevent user from blocking themselves
        if blocker.id == blocked.id:
            return Response({"error": "You cannot block yourself."}, status=400)

        # Check if user is already blocked
        if Block.objects.filter(blocker=blocker, blocked=blocked).exists():
            return Response({"message": f"{blocked.username} is already blocked."}, status=200)

        # Create block
        Block.objects.create(blocker=blocker, blocked=blocked)
        return Response({"message": f"{blocked.username} has been blocked."}, status=201)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_user(request):
    blocker = request.user
    blocked_id = request.data.get("blocked_id")

    # Check if unblock user ID is provided
    if not blocked_id:
        return Response({"error": "Blocked user ID is required."}, status=400)

    try:
        # Check if user exists
        blocked = User.objects.get(id=blocked_id)

        # Check if user is actually blocked
        block = Block.objects.filter(blocker=blocker, blocked=blocked).first()
        if not block:
            return Response({"error": f"{blocked.username} is not blocked."}, status=400)

        # Delete block
        block.delete()
        return Response({"message": f"{blocked.username} has been unblocked."}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_blocks(request):
    blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked__username', flat=True)
    return Response({"blocked_users": list(blocked_users)}, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateLanguage(request, pk):
    try:
        user = User.objects.get(id=pk)
        language = request.data.get('language')
        
        if language not in ['fr', 'en', 'ru', 'br']:
            return Response({'error': 'Invalid language'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.language = language
        user.save()
        
        return Response({
            'message': 'Language updated successfully',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
@permission_classes([AllowAny])
def fortytwo_login(request):
    """
    Initiate the 42 OAuth flow
    """
    client_id = settings.FORTYTWO_CLIENT_ID
    redirect_uri = 'http://localhost:8000/users/fortytwo/callback/'
    auth_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def fortytwo_callback(request):
    """
    Handle the 42 OAuth callback
    """
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'No code provided'}, status=400)

    # Exchange the code for an access token
    token_url = 'https://api.intra.42.fr/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.FORTYTWO_CLIENT_ID,
        'client_secret': settings.FORTYTWO_CLIENT_SECRET,
        'code': code,
        'redirect_uri': 'http://localhost:8000/users/fortytwo/callback/'
    }
    
    response = requests.post(token_url, data=data)
    if not response.ok:
        return Response({'error': 'Failed to get access token'}, status=400)

    access_token = response.json()['access_token']

    # Get user info from 42 API
    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_url, headers=headers)
    
    if not response.ok:
        return Response({'error': 'Failed to get user info'}, status=400)

    user_data = response.json()
    
    # Create or get user
    try:
        user = User.objects.get(id=pk)
        language = request.data.get('language')
        
        if language not in ['french', 'english', 'russian', 'breizh']:
            return Response({'error': 'Invalid language'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.language = language
        user.save()
        
        return Response({
            'message': 'Language updated successfully',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateTheme(request, pk):
    try:
        user = User.objects.get(id=pk)
        theme = request.data.get('theme')
        
        if theme not in ['dark', 'light', 'forest']:
            return Response({'error': 'Invalid theme'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.theme = theme
        user.save()
        
        return Response({
            'message': 'Theme updated successfully',
            'user': UserSerializer(user).data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend_by_username(request, username):
    try:
        user = request.user
        friend = User.objects.get(username=username)
        
        if user == friend:
            return Response({'error': 'You cannot add yourself as a friend'}, status=status.HTTP_400_BAD_REQUEST)
        
        if friend in user.friends.all():
            return Response({'error': 'This user is already your friend'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.add(friend)
        return Response({'message': f'Successfully added {friend.username} as friend'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend_by_username(request, username):
    try:
        user = request.user
        friend = User.objects.get(username=username)
        
        if friend not in user.friends.all():
            return Response({'error': 'This user is not in your friend list'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.friends.remove(friend)
        return Response({'message': f'Successfully removed {friend.username} from friends'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends_by_username(request, username=None):
    try:
        if username:
            user = User.objects.get(username=username)
        else:
            user = request.user
        
        friends = user.friends.all()
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def fortytwo_login(request):
    """
    Initiate the 42 OAuth flow
    """
    client_id = settings.FORTYTWO_CLIENT_ID
    redirect_uri = 'http://localhost:8000/users/fortytwo/callback/'
    auth_url = f'https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def fortytwo_callback(request):
    """
    Handle the 42 OAuth callback
    """
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'No code provided'}, status=400)

    # Exchange the code for an access token
    token_url = 'https://api.intra.42.fr/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.FORTYTWO_CLIENT_ID,
        'client_secret': settings.FORTYTWO_CLIENT_SECRET,
        'code': code,
        'redirect_uri': 'http://localhost:8000/users/fortytwo/callback/'
    }
    
    response = requests.post(token_url, data=data)
    if not response.ok:
        return Response({'error': 'Failed to get access token'}, status=400)

    access_token = response.json()['access_token']

    # Get user info from 42 API
    user_url = 'https://api.intra.42.fr/v2/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_url, headers=headers)
    
    if not response.ok:
        return Response({'error': 'Failed to get user info'}, status=400)

    user_data = response.json()
    
    # Create or get user
    try:
        user = User.objects.get(email=user_data['email'])
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=user_data['email'],
            username=user_data['login'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            password=None  # No password needed for OAuth
        )

    # Log the user in
    login(request._request, user)

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    response = redirect('http://localhost:5173')  # Redirect to frontend
    response.set_cookie(
        'access_token',
        access_token,
        max_age=3600,
        httponly=True,
        samesite='Lax'
    )
    response.set_cookie(
        'refresh_token',
        str(refresh),
        max_age=3600 * 24 * 7,
        httponly=True,
        samesite='Lax'
    )
    
    return response