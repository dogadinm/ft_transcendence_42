import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, PrivateMessage
from django.contrib.auth import get_user_model
from .game import room_manager
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from .models import User, Score, Friend, Message, ChatGroup, ScoreDoubleJack
from django.contrib.auth.hashers import check_password
from .doublejack import double_jack_table_manager
from .doublejack import GameStatus


class DoubleJackConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_elo_for_user(self, username):
        user = User.objects.get(username=username)  # Fetch the user object
        score = ScoreDoubleJack.objects.get(user=user)  # Fetch the related ScoreDoubleJack object
        return score
    async def connect(self):
        # Accept the WebSocket connection
        print(self.scope['url_route']['kwargs']['room_lobby'])
        self.room_name = self.scope['url_route']['kwargs']['room_lobby']
        self.room_group_name = f"ws_{self.room_name}"
        self.user = self.scope['user']
        self.username = self.user.username
        self.elo = await self.get_elo_for_user(self.username)
        
        # Get or create a room object
        self.table_game = double_jack_table_manager.get_or_create_table(self, self.room_name)
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
            self.elo = await self.get_elo_for_user(self.username)
            if (self.table_game.status == GameStatus.ENDED) :
                double_jack_table_manager.remove_table(self.room_name)
                self.table_game = double_jack_table_manager.get_or_create_table(self, self.room_name)
            if (self.username == ''): # maybe, need to check that guest cannot join the game
                return
            await self.send(text_data=json.dumps({
                'countdown': self.table_game.get_countdown_time()
            }))
            # get role here
            self.role = self.table_game.addPlayer(self.username, self.elo)
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
            print("HIT Action Triggered")
            bg_color = "#FFFF3F"
            await self.table_game.playerHit(self.role)
            print(f"Role after hit: {self.role}")
            if self.table_game.isPlayerStanding(self.role):
                bg_color = "#AAAA11"
                await self.send(text_data=json.dumps({
                    'disable': 'true'
                }))
            await self.send_player_info(self.role, bg_color)
            if (self.table_game.status == GameStatus.FINISHED) :
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
            await self.table_game.playerStand(self.role)
            # Send the color to the WebSocket
            # await self.send(text_data=json.dumps({
            #     'color': bg_color
            # }))
            if self.table_game.isPlayerStanding(self.role):
                await self.send(text_data=json.dumps({
                    'disable': 'true'
                }))
            await self.send_player_info(self.role, bg_color)
            if (self.table_game.status == GameStatus.FINISHED) :
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