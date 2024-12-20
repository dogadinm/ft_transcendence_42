import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, PrivateMessage
from django.contrib.auth import get_user_model
from .game import room_manager
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, Message, ChatGroup
from django.contrib.auth.hashers import check_password
from .doublejack import double_jack_table_manager

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

    async def send_player_info(self, role, bg_color):
        # """Helper method to send player information to the WebSocket group."""
        player_info = {
            'role': role,
            'name': self.table_game.playerName(role),
            'status': self.table_game.playerStatus(role),
            'points': self.table_game.playerPoints(role),
            'hand': self.table_game.playerHand(role),
            'score': self.table_game.playerScore(role),
            'color': bg_color
        }
        await self.channel_layer.group_send(self.room_group_name, {'type': 'update', **player_info})
    async def handle_role_and_send_info(self, bg_color, adjacent_role=None):
        await self.send_player_info(self.role, bg_color)
        if adjacent_role is not None:
            await self.send_player_info(adjacent_role, bg_color)
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "join":
            if (self.username == ''): # maybe, need to check that guest cannot join the game
                return
            await self.send(text_data=json.dumps({
                'countdown': self.table_game.get_countdown_time()
            }))
            # get role here
            self.role = self.table_game.addPlayer(self.username, 1000)
            print("join")
            print(self.role)
            bg_color = "#007F00"
            await self.send(text_data=json.dumps({
                'type': 'join',
                'joined': self.role,
                'set': 'set',
                'role': self.role,
                'name': self.table_game.playerName(self.role),
                'status': self.table_game.playerStatus(self.role),
                'points': self.table_game.playerPoints(self.role),
                'hand': self.table_game.playerHand(self.role),
                'score': self.table_game.playerScore(self.role),
                'color': bg_color
                }))
            if self.role == 2 :
                await self.send_player_info(self.role, bg_color)
                await self.send_player_info(self.role - 1, bg_color)
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
            await self.send_player_info(self.role, bg_color)
            await self.handle_role_and_send_info(bg_color, self.role - 1 if self.role == 2 else self.role + 1)
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
            await self.send_player_info(self.role, bg_color)
            if (self.table_game.status == 4) :
                print("hit 4")
                await self.channel_layer.group_send(
                self.room_group_name,
                    {
                        'type': 'reset',
                        'reset': 'reset'
                    }
                )
                await self.handle_role_and_send_info(bg_color, self.role - 1 if self.role == 2 else self.role + 1)
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
            await self.send_player_info(self.role, bg_color)
            if (self.table_game.status == 4) :
                print("stay 4")
                await self.channel_layer.group_send(
                self.room_group_name,
                    {
                        'type': 'reset',
                        'reset': 'reset'
                    }
                )
                await self.handle_role_and_send_info(bg_color, self.role - 1 if self.role == 2 else self.role + 1)
    async def update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update',
            'role': event['role'],
            'name': event['name'],
            'status': event['status'],
            'points': event['points'],
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
        room_name = event['room_name']
        if room_name == self.room_name:
            # Send the countdown message to the client (only for the relevant room)
            await self.send(text_data=json.dumps({
                'countdown': countdown
            }))

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.user = self.scope['user']
        self.username = self.user.username

        # Connect the user to the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Get or create a room object
        self.room_game = room_manager.get_or_create_room(self.room_name)
        self.role = await self.assign_role()

        await self.send(json.dumps({'type': 'role_assignment', 'role': self.role}))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Free up space if a player disconnects
        if self.room_game.players['left'] == self.username:
            self.room_game.players['left'] = None
            self.room_game.ready['left'] = False
        elif self.room_game.players['right'] == self.username:
            self.room_game.players['right'] = None
            self.room_game.ready['right'] = False
        if self.room_game.players['right'] == None and self.room_game.players['left'] == None:
            room_manager.remove_room(self.room_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        direction = data.get('direction')

        if action == 'ready':
            if self.role == 'left':
                self.room_game.ready['left'] = True
            elif self.role == 'right':
                self.room_game.ready['right'] = True

            if self.room_game.ready['left'] and self.room_game.ready['right']:
                asyncio.create_task(self.room_game.game_loop(self.send_game_update))


        elif action == 'move':
            if self.role == 'left':
                self.room_game.paddles['left']['direction'] = -1 if direction == 'up' else 1
            elif self.role == 'right':
                self.room_game.paddles['right']['direction'] = -1 if direction == 'up' else 1
        elif action == 'stop':
            if self.role == 'left' and direction in ['up', 'down']:
                self.room_game.paddles['left']['direction'] = 0
            elif self.role == 'right' and direction in ['up', 'down']:
                self.room_game.paddles['right']['direction'] = 0

        elif action == 'repeat':
            self.room_game.score = {'left': 0, 'right': 0}
            await self.send(json.dumps({'type': 'role_assignment', 'role': self.role}))



    async def send_game_update(self, game_state):
        # print("Sending game update:", game_state)
        winner = self.room_game.end_game()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': game_state
            }
        )
        if winner:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_over',
                    'winner': winner,
                }
            )


    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'paddles': event['game_state']['paddles'],
            'ball': event['game_state']['ball'],
            'score': event['game_state']['score']
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner']
        }))

    async def assign_role(self):
        if not self.room_game.players['left']:
            self.room_game.players['left'] = self.username
            return 'left'
        elif not self.room_game.players['right']:
            self.room_game.players['right'] = self.username
            return 'right'
        return 'spectator'

