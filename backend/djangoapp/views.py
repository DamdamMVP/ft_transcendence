from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import User, History, Block
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, HistorySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    user = authenticate(request, username=email, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            'message': 'User authenticated',
            'user': UserSerializer(user).data,
        }, status=200)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,  # Rend le cookie inaccessible en JavaScript
            secure=True,  # En production, active cette option pour HTTPS uniquement
            samesite='Strict',  # Restreint le cookie aux mêmes origines (protection CSRF)
            max_age=60 * 5  # Temps de vie du token (en secondes)
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=60 * 60 * 24
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
            'message': 'Access token refreshed successfully'
        }, status=200)

        # Met à jour le cookie d'accès
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=60 * 5  # Temps de vie du token d'accès
        )
        return response
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=400)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    response = Response({'message': 'Logged out successfully'}, status=200)

    # Supprimer les cookies
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response


# Obtenir tous les utilisateurs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getData(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# Obtenir un utilisateur spécifique
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# Ajouter un nouvel utilisateur (avec hachage du mot de passe)
@api_view(['POST'])
@permission_classes([AllowAny])  # Autorise l'accès sans authentification
def addUser(request):
    data = request.data

    # Hacher le mot de passe
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
        user = User.objects.get(id=pk)
        data = request.data

        # Si un mot de passe est fourni, le hacher
        if 'password' in data:
            data['password'] = make_password(data['password'])

        serializer = UserSerializer(instance=user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


# Supprimer un utilisateur
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response({'message': 'User successfully deleted!'}, status=200)

# Connexion utilisateur
@api_view(['GET'])
@permission_classes([AllowAny])
def connect(request):
    return render(request, 'login.html')


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateProfilePicture(request, pk):
    try:
        user = User.objects.get(id=pk)

        if 'profile_picture' not in request.FILES:
            return Response({'error': 'No profile picture provided'}, status=400)

        # Mettre à jour la photo de profil
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

        data['password'] = make_password(data['password'])
        serializer = UserSerializer(instance=user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password updated successfully'}, status=200)
        return Response(serializer.errors, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getHistories(request):
    histories = History.objects.all()
    serializer = HistorySerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserHistory(request, user_id):
    histories = History.objects.filter(user_id=user_id)
    serializer = HistorySerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addHistory(request):
    serializer = HistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateHistory(request, pk):
    history = History.objects.get(id=pk)
    serializer = HistorySerializer(instance=history, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteHistory(request, pk):
    history = History.objects.get(id=pk)
    history.delete()
    return Response({'message': 'History successfully deleted!'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request):
    blocker = request.user
    blocked_id = request.data.get("blocked_id")

    try:
        blocked = User.objects.get(id=blocked_id)
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

    try:
        blocked = User.objects.get(id=blocked_id)
        Block.objects.filter(blocker=blocker, blocked=blocked).delete()
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
