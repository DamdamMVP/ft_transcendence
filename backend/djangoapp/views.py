from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import check_password, make_password
from .models import User, Block
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserStatus
from django.conf import settings
import requests
import secrets
import string
import urllib.parse
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def online_users(request):
    online_users = UserStatus.objects.filter(is_online=True).values("user__id", "user__username")
    return Response({"online_users": list(online_users)}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def anonymiseUser(request):
    user = request.user
    if not user:
        return Response({"error": "User not found"}, status=404)
    if user.username == "Anonymous":
        return Response({"error": "User is already anonymized"}, status=400)
    user.username = f"Anonymous_{user.id}"
    user.email = f"anonymous_{user.id}@gmail.com"
    user.save()
    return Response({"message": "User anonymized successfully"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    user = authenticate(request, username=email, password=password)

    if user:
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
            max_age=3600 * 24
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='None',
            max_age= 3600 * 24 * 7
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
            max_age=60 * 60 * 24
        )
        return response
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=400)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    status, _ = UserStatus.objects.get_or_create(user=user)
    status.is_online = False
    status.save()

    response = Response({'message': 'Logged out successfully'}, status=200)

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

# Add a new user
@api_view(['POST'])
@permission_classes([AllowAny])
def addUser(request):
    data = request.data

    password = data.get('password')

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Hash password
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
        # Check if request user = user to be updated
        if int(request.user.id) != int(pk):
            return Response({'error': 'You can only update your own account.'}, status=403)
        
        user = request.user
        data = request.data

        allowed_fields = ['username', 'email']
        update_data = {field: data[field] for field in allowed_fields if field in data}

        if not update_data:
            return Response({'error': 'Only username and email can be updated.'}, status=400)

        serializer = UserSerializer(instance=user, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    user = request.user
    user.delete()
    return Response({'message': 'User successfully deleted!'}, status=200)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateProfilePicture(request, pk):
    try:
        user = request.user
        if 'profile_picture' not in request.FILES:
            return Response({'error': 'No profile picture provided'}, status=400)

        user.profile_picture = request.FILES['profile_picture']
        user.save()

        return Response({'message': 'Profile picture updated successfully'}, status=200)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePassword(request, pk):
    try:
        user = request.user
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
        user = request.user
        theme = request.data.get('theme')
        
        if theme not in ['dark', 'light', 'forest', 'coffee', 'neon', 'mint']:
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

    if not blocked_id:
        return Response({"error": "Blocked user ID is required."}, status=400)

    try:
        # Check if user exists
        blocked = User.objects.get(id=blocked_id)

        if blocker.id == blocked.id:
            return Response({"error": "You cannot block yourself."}, status=400)

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

    if not blocked_id:
        return Response({"error": "Blocked user ID is required."}, status=400)

    try:
        # Check if user exists
        blocked = User.objects.get(id=blocked_id)

        block = Block.objects.filter(blocker=blocker, blocked=blocked).first()
        if not block:
            return Response({"error": f"{blocked.username} is not blocked."}, status=400)

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
        
        if language not in ['fr', 'en', 'ru', 'br', 'it']:
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
        
        if theme not in ['dark', 'light', 'forest', 'coffee', 'neon', 'mint']:
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
    hostname = settings.HOSTNAME
    redirect_uri = f'https://{hostname}:8443/users/fortytwo/callback/'
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
        'redirect_uri': f'https://{settings.HOSTNAME}:8443/users/fortytwo/callback/'
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
   
    try:
        user = User.objects.get(email=user_data['email'])
    except User.DoesNotExist:
        random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        user = User.objects.create_user(
            email = user_data['email'],
            username = user_data['login'],
            first_name = user_data.get('first_name', ''),
            last_name = user_data.get('last_name', ''),
            password = random_password 
        )

    # Get 42 profile picture
    if 'image' in user_data and 'link' in user_data['image']:
        image_url = user_data['image']['link']
        
        image_response = requests.get(image_url)
        
        if image_response.ok:
            from django.core.files.base import ContentFile
            import os
            
            image_name = f"42_profile_{user.username}{os.path.splitext(image_url)[1]}"
            
            user.profile_picture.save(
                image_name,
                ContentFile(image_response.content),
                save=True
            )
        else:
            print("Failed to download image:", image_response.text)
    else:
        print("No image URL found in user data")

    # Auth and connect the user
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request._request, user)

    # Create JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    print(f"User authentication status: {user.is_authenticated}")
    print(f"Current user: {user.username}")

    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'profile_picture': user.profile_picture.url if user.profile_picture else None,
        'language': user.language,
        'theme': user.theme,
    }
    
    frontend_url = f'https://{settings.HOSTNAME}:8443/auth-callback?user={urllib.parse.quote(json.dumps(user_data))}&token={access_token}'
    response = redirect(frontend_url)
    
    response.set_cookie(
        'access_token',
        access_token,
        max_age=3600 * 24,
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