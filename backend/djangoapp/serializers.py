from rest_framework import serializers
from .models import User, History

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'user', 'guest_name', 'user_score', 'guest_score', 'played_at', 'game_name']

class UserSerializer(serializers.ModelSerializer):
    histories = HistorySerializer(many=True, read_only=True) 
    friends = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'histories', 'profile_picture', 'language', 'theme', 'friends']
        extra_kwargs = {
            'password': {'write_only': True},
        }
