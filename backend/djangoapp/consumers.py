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
    
    @database_sync_to_async
    def get_blocked_users(self, user):
            """
            Function to retrieve IDs of users blocked by the current user.
            """
            return list(Block.objects.filter(blocker=user).values_list("blocked_id", flat=True))