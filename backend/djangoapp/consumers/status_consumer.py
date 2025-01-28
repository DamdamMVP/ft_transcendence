import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from ..models import UserStatus

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
