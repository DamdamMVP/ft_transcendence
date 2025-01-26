from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import History
from .serializers import HistorySerializer

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
