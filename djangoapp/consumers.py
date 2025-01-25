import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from . import models
from datetime import datetime

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # extract the token from the query parameters
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]

        if not token:
            await self.close()
            return

        try:
            # Validate token JWT
            decoded_token = UntypedToken(token)
            # extraxt user_id from the token
            user_id = decoded_token["user_id"]
            # get user from the database
            self.scope["user"] = await database_sync_to_async(User.objects.get)(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            await self.close()
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
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = data.get('message')
        if not message or not message.strip():
            return

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].username,
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))
