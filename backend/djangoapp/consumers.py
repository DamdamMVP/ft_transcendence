import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Block, UserStatus  # Modèle pour les statuts
from django.contrib.auth.models import AnonymousUser
from datetime import datetime

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if isinstance(user, AnonymousUser):
            await self.close(code=4001)  # WebSocket code for unauthorized user
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
            if str(user.username) not in [user1, user2]:
                await self.close()
                return

        # Mark user as online
        await self.set_user_online(user)

        # Add user to room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify group that user has connected
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': user.id,
                'username': user.username,
                'is_online': True,
            }
        )

    async def disconnect(self, close_code):
        user = self.scope["user"]

        # Mark user as offline
        await self.set_user_offline(user)

        # Notify group that user has disconnected
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': user.id,
                'username': user.username,
                'is_online': False,
            }
        )

        # Remove user from room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        user = self.scope["user"]  # Connected user

        # Decode message data
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = data.get('message')
        if not message or not message.strip():
            return

        # Send the message to the group
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'sender_id': user.id,  # Adding ID for block management
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        user = self.scope["user"]
        sender_id = event['sender_id']
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Check if user has blocked the sender
        blocked_senders = await self.get_blocked_users(user)

        # If current user (`user`) has blocked the sender (`sender_id`), ignore message
        if sender_id in blocked_senders:
            return

        # Send message to user
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))

    async def user_status(self, event):
        """
        Notify all users in the group about the status change of a user.
        """
        await self.send(text_data=json.dumps({
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online'],
        }))

    @database_sync_to_async
    def set_user_online(self, user):
        """
        Set the user status to online.
        """
        UserStatus.objects.update_or_create(user=user, defaults={'is_online': True})

    @database_sync_to_async
    def set_user_offline(self, user):
        """
        Set the user status to offline.
        """
        UserStatus.objects.filter(user=user).update(is_online=False)

    @database_sync_to_async
    def get_blocked_users(self, user):
        """
        Function to retrieve IDs of users blocked by the current user.
        """
        return list(Block.objects.filter(blocker=user).values_list("blocked_id", flat=True))
<<<<<<< HEAD


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("status", self.channel_name)
        await self.accept()
        if self.scope["user"].is_authenticated:
            status_update = await self.update_user_status(True)
            await self.channel_layer.group_send("status", status_update)
            
    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            status_update = await self.update_user_status(False)
            await self.channel_layer.group_send("status", status_update)
        await self.channel_layer.group_discard("status", self.channel_name)

    @database_sync_to_async
    def update_user_status(self, is_online):
        user = self.scope["user"]
        status, _ = UserStatus.objects.get_or_create(user=user)
        status.is_online = is_online
        status.save()
        
        return {
            "type": "user_status",
            "user_id": user.id,
            "is_online": is_online
        }

    async def user_status(self, event):
        # Envoyer la mise à jour du statut à tous les clients connectés
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "user_id": event["user_id"],
            "is_online": event["is_online"]
        }))

=======
>>>>>>> 7845085 (+: add online status via websocket)
