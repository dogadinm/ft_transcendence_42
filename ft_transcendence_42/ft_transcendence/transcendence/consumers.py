import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room
from django.contrib.auth import get_user_model
from .game import room_manager
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, Message, ChatGroup

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

        # Send the assigned role to the user
        await self.send(json.dumps({'type': 'role_assignment', 'role': self.role}))

        # Start the game loop if it is not already running



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



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.username = self.user.username

        second_user_id = 10
        self.room_group_name = self.create_room_name(self.user.id, second_user_id)


        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        who = text_data_json.get('who')




        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message
            }
        )


    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'chat',
            'message':message,
        }))

    @staticmethod
    def create_room_name(user1_id, user2_id):
        return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

class ChatGroupConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_nick = self.scope['url_route']['kwargs']['channel_nick']
        self.channel_group_name = f'game_{self.channel_nick}'
        self.user = self.scope['user']
        self.username = self.user.username

        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name, self.channel_name
        )
        self.accept()


        self.chat_group = ChatGroup.objects.get(name=self.channel_nick)

        if not (self.user in self.chat_group.members.all() or self.user == self.chat_group.owner):
            self.send(text_data=json.dumps({
                'type': 'join',
                'messages': 'Join to the chat',
            }))
            return

        blocked_users = self.user.blocked_users.all()
        messagesql = Message.objects.filter(chat=self.chat_group).exclude(sender__in=blocked_users).order_by("created_at")

        messages_data = [
            {
                "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                "sender": message.sender.nickname,
                "message": message.text,
                "photo": message.sender.photo.url if message.sender.photo else 'profile_photos/profile_standard.jpg',
            }
            for message in messagesql
        ]

        self.send(text_data=json.dumps({
            'type': 'chat',
            'messages': messages_data,
        }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'join':
            self.chat_group.members.add(self.user)
            return
        elif action == 'leave':
            self.chat_group.members.remove(self.user)
            return
        message_text = text_data_json.get('message', '').strip()

        if not message_text:
            return

        messagesql = Message.objects.create(chat=self.chat_group, sender=self.user, text=message_text)

        message_data = {
            "time": messagesql.created_at.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
            "sender": messagesql.sender.nickname,
            "message": messagesql.text,
            "photo": messagesql.sender.photo.url if messagesql.sender.photo else 'profile_photos/profile_standard.jpg',
        }

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'chat_message',
                'message': message_data,
            }
        )

    def chat_message(self, event):
        message = event['message']

        sender_nickname = message['sender']
        sender_user = User.objects.filter(nickname=sender_nickname).first()
        if sender_user in self.user.blocked_users.all():
            return

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))