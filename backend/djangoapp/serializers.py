from rest_framework import serializers
from .models import User, History

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'guest_name', 'user_score', 'guest_score', 'played_at', 'game_name']

class UserSerializer(serializers.ModelSerializer):
    histories = HistorySerializer(many=True, read_only=True)  # Relation avec History
    friends = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Liste des IDs des amis

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'histories', 'profile_picture', 'language', 'theme', 'friends']  # Ajout de friends
        extra_kwargs = {
            'password': {'write_only': True},  # Cache le mot de passe lors de la lecture
        }
