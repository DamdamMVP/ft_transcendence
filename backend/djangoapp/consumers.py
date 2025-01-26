import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from . import models
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from .models import Block

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4001)  # Code WebSocket pour utilisateur non autorisé
            return

        # get chan name from the url
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        if self.room_name.startswith("private_"):
            try:
                _, user1, user2 = self.room_name.split("_")
            except ValueError:
                await self.close()
                return

            # check if the user is part of the private chat
            if str(self.scope['user'].username) not in [user1, user2]:
                await self.close()
                return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def get_blocked_by_users(self, user):
        """
        Récupère les utilisateurs qui ont bloqué l'utilisateur actuel.
        """
        return list(Block.objects.filter(blocked=user).values_list("blocker_id", flat=True))

    async def receive(self, text_data):
        user = self.scope["user"]  # Utilisateur connecté

        # Décoder les données du message
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = data.get('message')
        if not message or not message.strip():
            return

        # Envoyer le message au groupe
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'sender_id': user.id,  # Ajout de l'ID pour gérer les blocs
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        user = self.scope["user"]
        message = event['message']
        sender = event['sender']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        # Obtenir les utilisateurs qui ont bloqué l'utilisateur actuel
        blocked_by_users = await self.get_blocked_by_users(user)

        # Debug : Afficher les utilisateurs qui ont bloqué l'utilisateur actuel
        print(f"Utilisateur {user.id} est bloqué par : {blocked_by_users}")

        # Ne pas envoyer le message si l'utilisateur qui envoie le message est bloqué
        if sender_id in blocked_by_users:
            return

        # Envoyer le message au client
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))