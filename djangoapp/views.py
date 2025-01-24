from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import User, History
from django.contrib.auth import authenticate
from .serializers import UserSerializer, HistorySerializer

# Obtenir tous les utilisateurs
@api_view(['GET'])
def getData(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# Obtenir un utilisateur spécifique
@api_view(['GET'])
def getUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# Ajouter un nouvel utilisateur (avec hachage du mot de passe)
@api_view(['POST'])
def addUser(request):
    data = request.data

    # Hacher le mot de passe avant de le sauvegarder
    data['password'] = make_password(data['password'])
    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
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
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response({'message': 'User successfully deleted!'}, status=200)

# Connexion utilisateur
@api_view(['POST'])
def connect(request):
    data = request.data

    email = data.get('email')
    password = data.get('password')

    # Utiliser authenticate pour vérifier l'utilisateur
    user = authenticate(request, username=email, password=password)

    if user:
        serializer = UserSerializer(user)
        return Response({
            'message': 'User authenticated',
            'user': serializer.data
        }, status=200)
    return Response({'error': 'Invalid email or password'}, status=400)


@api_view(['GET'])
def getHistories(request):
    histories = History.objects.all()
    serializer = HistorySerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getUserHistory(request, user_id):
    histories = History.objects.filter(user_id=user_id)
    serializer = HistorySerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addHistory(request):
    serializer = HistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def updateHistory(request, pk):
    history = History.objects.get(id=pk)
    serializer = HistorySerializer(instance=history, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def deleteHistory(request, pk):
    history = History.objects.get(id=pk)
    history.delete()
    return Response({'message': 'History successfully deleted!'}, status=200)
