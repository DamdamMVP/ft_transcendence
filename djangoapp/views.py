from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import User, History
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, HistorySerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from rest_framework import status


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

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    # Utiliser authenticate pour vérifier l'utilisateur
    user = authenticate(request, username=email, password=password)

    if user:
        serializer = UserSerializer(user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User authenticated',
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)
    return Response({'error': 'Invalid email or password'}, status=400)

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
