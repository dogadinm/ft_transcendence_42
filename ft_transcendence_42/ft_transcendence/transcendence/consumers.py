import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room
from django.contrib.auth import get_user_model
from .doublejack import double_jack_table_manager

User = get_user_model()

# dj_users = ['']

class DoubleJackConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        self.room_name = "double_jack_room"
        self.room_group_name = f"ws_{self.room_name}"
        self.user = self.scope['user']
        self.username = self.user.username
        print(self.username)
        # Get or create a room object
        self.table_game = double_jack_table_manager.get_or_create_table(self.room_name)
        # self.role = await self.assign_dj_role()
        
        # print(self.role)
        # Connect the user to the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # Start the countdown task
        # self.countdown_task = asyncio.create_task(self.start_countdown())

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Cancel the countdown task if it's still running
        # if self.countdown_task:
        #     self.countdown_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "join":
            await self.send(text_data=json.dumps({
                'countdown': self.table_game.get_countdown_time()
            }))
            # get role here
            self.role = self.table_game.addPlayer(self.username, 1000)
            print("join")
            bg_color = "#007F00"
            await self.send(text_data=json.dumps({
            'type': 'join',
            'joined': self.role,
            'set' : 'set',
            'name': self.username,
            'role': self.role,
            'hand': self.table_game.playerHand(self.role),
            'score': self.table_game.playerScore(self.role),
            'color': bg_color
            }))
            if self.role == 2 :
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update',
                        'role': self.role,
                        'hand': self.table_game.playerHand(self.role),
                        'score': self.table_game.playerScore(self.role),
                        'color': bg_color
                    })
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update',
                        'role': self.role - 1,
                        'hand': self.table_game.playerHand(self.role - 1),
                        'score': self.table_game.playerScore(self.role - 1),
                        'color': bg_color
                    })
        if data.get("action") == "reset":
            print("reset")
            if not self.table_game.is_running:
                asyncio.create_task(self.table_game.start_countdown())
            bg_color = "#337F00"
            self.table_game.reset()
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'set',
                'set' : 'set'
            })
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update',
                'role': self.role,
                'hand': self.table_game.playerHand(self.role),
                'score': self.table_game.playerScore(self.role),
                'color': bg_color
            })
            if self.role == 2 :
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update',
                    'role': self.role - 1,
                    'hand': self.table_game.playerHand(self.role - 1),
                    'score': self.table_game.playerScore(self.role - 1),
                    'color': bg_color
                })
            else :
                await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update',
                    'role': self.role + 1,
                    'hand': self.table_game.playerHand(self.role + 1),
                    'score': self.table_game.playerScore(self.role + 1),
                    'color': bg_color
                })
        if data.get("action") == "hit":
            print("hit")
            bg_color = "#FFFF3F"
            self.table_game.playerHit(self.role)
            # Send the color to the WebSocket
            if self.table_game.isPlayerStanding(self.role):
                bg_color = "#AAAA11"
                await self.send(text_data=json.dumps({
                    'disable': 'true'
                }))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update',
                    'role': self.role,
                    'hand': self.table_game.playerHand(self.role),
                    'score': self.table_game.playerScore(self.role),
                    'color': bg_color
                }
            )
            if (self.table_game.status == 4) :
                print("hit 4")
                await self.channel_layer.group_send(
                self.room_group_name,
                    {
                        'type': 'reset',
                        'reset': 'reset'
                    }
            )
        elif data.get("action") == "stay":
            print("stay")
            print(self.role)
            # print(self.table_game.isPlayerStanding(self.role))
            bg_color = "#CC3333"
            self.table_game.playerStand(self.role)
            # Send the color to the WebSocket
            # await self.send(text_data=json.dumps({
            #     'color': bg_color
            # }))
            if self.table_game.isPlayerStanding(self.role):
                await self.send(text_data=json.dumps({
                    'disable': 'true'
                }))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update',
                    'role': self.role,
                    'hand': self.table_game.playerHand(self.role),
                    'score': self.table_game.playerScore(self.role),
                    'color': bg_color
                }
            )
            if (self.table_game.status == 4) :
                print("stay 4")
                await self.channel_layer.group_send(
                self.room_group_name,
                    {
                        'type': 'reset',
                        'reset': 'reset'
                    }
            )
    async def update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update',
            'role': event['role'],
            'hand': event['hand'],
            'score': event['score'],
            'color': event['color']
        }))
    async def reset(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reset',
            'reset': event['reset']
        }))
    async def set(self, event):
        await self.send(text_data=json.dumps({
            'type': 'set',
            'set': event['set']
        }))
    async def send_countdown(self, event):
        # """Receive a message from the group and send it to the WebSocket client."""
        # The event will contain the countdown time and possibly a message
        countdown = event['countdown']
        message = event.get('message', '')
        room_name = event['room_name']
        print("SEND_COUNTDOWN")
        if room_name == self.room_name:
            # Send the countdown message to the client (only for the relevant room)
            await self.send(text_data=json.dumps({
                'countdown': countdown
            }))
    # async def assign_dj_role(self):
    #     if self.username not in dj_users:
    #         dj_users.append(self.username)
    #     return dj_users.index(self.username)

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
