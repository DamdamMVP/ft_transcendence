from rest_framework import serializers
from .models import User, History

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'guest_name', 'user_score', 'guest_score', 'played_at']

class UserSerializer(serializers.ModelSerializer):
    histories = HistorySerializer(many=True, read_only=True)  # Relation avec History

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'histories', 'profile_picture']  # Ajout de histories
        extra_kwargs = {
            'password': {'write_only': True},  # Cache le mot de passe lors de la lecture
        }
