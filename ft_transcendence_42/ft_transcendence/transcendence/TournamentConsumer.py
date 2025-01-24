import json
from traceback import print_tb
import random
import string
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, Message, ChatGroup, PrivateMessage
from .game import room_manager

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']

        await self.channel_layer.group_add("status_updates", self.channel_name)
        await self.accept()




    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_lobby_name, self.channel_name)

    async def receive(self, text_data):
        print('hello')


