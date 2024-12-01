import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room
from django.contrib.auth import get_user_model
# from .doublejack import double_jack_table_manager

User = get_user_model()

class DoubleJackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        self.room_name = "double_jack_room"
        self.room_group_name = f"ws_{self.room_name}"
        # Connect the user to the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get("action") == "change_color":
            # Generate a random color
            random_color = f"#{random.randint(0, 0xFFFFFF):06x}"

            # Send the color to the WebSocket
            await self.send(text_data=json.dumps({
                'color': random_color
            }))
        elif data.get("action") == "change_color_for_all":
            # Generate a fixed color
            random_color = f"#{random.randint(0, 0xFFFFFF):06x}"

            # Send the color to the WebSocket
            await self.send(text_data=json.dumps({
                'color': random_color
            }))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'test',
                    'color': random_color
                }
            )

    async def test(self, event):
        await self.send(text_data=json.dumps({
            'type': 'test',
            'color': event['color']
        }))

class GameLogic(AsyncWebsocketConsumer):
    players = {'left': None, 'right': None}
    paddles = {'left': {'paddleY': 150}, 'right': {'paddleY': 150}}
    ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
    score = {'player1': 0, 'player2': 0}
    game_loop_running = False

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        
        self.room, created = await self.get_or_create_room(self.room_name)

        if not GameLogic.players['left']:
            GameLogic.players['left'] = self.channel_name
            self.role = 'player1'
        elif not GameLogic.players['right']:
            GameLogic.players['right'] = self.channel_name
            self.role = 'player2'
        else:
            self.role = 'spectator'

        await self.send(json.dumps({'type': 'role_assignment', 'role': self.role}))

        if not GameLogic.game_loop_running:
            GameLogic.game_loop_running = True
            asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.role == 'player1' and GameLogic.players['left'] == self.channel_name:
            GameLogic.players['left'] = None
        elif self.role == 'player2' and GameLogic.players['right'] == self.channel_name:
            GameLogic.players['right'] = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        paddle_y = data.get('paddleY')

        if self.role == 'player1':
            GameLogic.paddles['left']['paddleY'] = paddle_y
        elif self.role == 'player2':
            GameLogic.paddles['right']['paddleY'] = paddle_y

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'paddles': GameLogic.paddles,
                'ball': GameLogic.ball,
                'score': GameLogic.score,
            }
        )

    async def game_loop(self):
        while True:

            GameLogic.ball['x'] += GameLogic.ball['dx']
            GameLogic.ball['y'] += GameLogic.ball['dy']


            if GameLogic.ball['y'] <= 0 or GameLogic.ball['y'] >= 400:
                GameLogic.ball['dy'] *= -1

    
            for side, paddle in GameLogic.paddles.items():
                paddle_x = 10 if side == 'left' else 780
                if paddle_x < GameLogic.ball['x'] < paddle_x + 10:
                    if paddle['paddleY'] < GameLogic.ball['y'] < paddle['paddleY'] + 100:
                        GameLogic.ball['dx'] *= -1

            if GameLogic.ball['x'] <= 0:
                GameLogic.score['player2'] += 1
                await self.reset_ball()
            elif GameLogic.ball['x'] >= 800:
                GameLogic.score['player1'] += 1
                await self.reset_ball()


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'paddles': GameLogic.paddles,
                    'ball': GameLogic.ball,
                    'score': GameLogic.score,
                }
            )
            await asyncio.sleep(0.03)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def reset_ball(self):
        GameLogic.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}

    @database_sync_to_async
    def get_or_create_room(self, room_name):
        return Room.objects.get_or_create(name=room_name)
