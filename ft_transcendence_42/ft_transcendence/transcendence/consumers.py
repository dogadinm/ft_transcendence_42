import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room
from django.contrib.auth import get_user_model
from .game import room_manager

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']

        # Connect the user to the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Get or create a room object
        self.room_game = room_manager.get_or_create_room(self.room_name)
        self.role = await self.assign_role()

        # Send the assigned role to the user
        await self.send(json.dumps({'type': 'role_assignment', 'role': self.role}))

        # Start the game loop if it is not already running
        if not self.room_game.game_loop_running:
            self.room_game.game_loop_running = True
            asyncio.create_task(self.room_game.game_loop(self.send_game_update))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Free up space if a player disconnects
        if self.role == 'player1':
            self.room_game.players['left'] = None
        elif self.role == 'player2':
            self.room_game.players['right'] = None
        if self.room_game.players['right'] == None and self.room_game.players['left'] == None:
            room_manager.remove_room(self.room_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        direction = data.get('direction')

        if action == 'move':
            if self.role == 'player1' and direction == 'up':
                self.room_game.paddles['left']['direction'] = -1
            elif self.role == 'player1' and direction == 'down':
                self.room_game.paddles['left']['direction'] = 1
            elif self.role == 'player2' and direction == 'up':
                self.room_game.paddles['right']['direction'] = -1
            elif self.role == 'player2' and direction == 'down':
                self.room_game.paddles['right']['direction'] = 1
        elif action == 'stop':
            if self.role == 'player1' and direction in ['up', 'down']:
                self.room_game.paddles['left']['direction'] = 0
            elif self.role == 'player2' and direction in ['up', 'down']:
                self.room_game.paddles['right']['direction'] = 0

    async def send_game_update(self, game_state):
        # print("Sending game update:", game_state)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': game_state
            }
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'paddles': event['game_state']['paddles'],
            'ball': event['game_state']['ball'],
            'score': event['game_state']['score']
        }))

    async def assign_role(self):
        if not self.room_game.players['left']:
            self.room_game.players['left'] = self.channel_name
            return 'player1'
        elif not self.room_game.players['right']:
            self.room_game.players['right'] = self.channel_name
            return 'player2'
        return 'spectator'
