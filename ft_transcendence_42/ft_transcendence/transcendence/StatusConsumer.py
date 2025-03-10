from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from .models import Friend
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

user_status_set = set()

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if(self.user in user_status_set):
            return

        user_status_set.add(self.user)
        await self.channel_layer.group_add("status_updates", self.channel_name)
        await self.accept()

        self.keep_sending_status = True
        self.periodic_task = asyncio.create_task(self.send_online_status())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("status_updates", self.channel_name)
        self.keep_sending_status = False
        user_status_set.remove(self.user )
        if hasattr(self, "periodic_task"):
            self.periodic_task.cancel()

    async def send_online_status(self):
        while self.keep_sending_status:
            online_users = await self.get_online_users()

            await self.send(text_data=json.dumps({
                "type": "user_status",
                "users": online_users,
                "is_online": True,
            }))
            await asyncio.sleep(30)
   

    async def user_status(self, event):

        await self.send(text_data=json.dumps({
            "type": "user_status",
            "username": event["username"],
            "is_online": event["is_online"],
        }))

    @sync_to_async
    def get_online_users(self):
        friend_objct = get_object_or_404(Friend, owner=self.user)
        friends = friend_objct.friends.filter(is_online=True).values_list("username", flat=True)
        return list(friends)
