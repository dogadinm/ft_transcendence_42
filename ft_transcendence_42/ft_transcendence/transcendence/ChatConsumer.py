import json
import random
import string
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, PrivateMessage
from .game import room_manager

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.friend_username = self.scope['url_route']['kwargs']['friend_username']

        if not Friend.objects.filter(owner=self.user, friends__username=self.friend_username).exists() and self.friend_username != "chatbot":
            return

        self.room_name = self.create_room_name(self.user.username, self.friend_username)
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

        blocked_users = self.user.blocked_users.all()

        friend = User.objects.get(username=self.friend_username)
        messages = PrivateMessage.objects.filter(
            sender__in=[self.user, friend],
            receiver__in=[self.user, friend]
        ).exclude(sender__in=blocked_users).order_by('created_at')

        messages_data = [
            {
                'sender': message.sender.username,
                'message': message.text,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for message in messages
        ]
        self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': messages_data,
        }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        invite = data.get('invite')
        friend = User.objects.get(username=self.friend_username)
        if not Friend.objects.filter(owner=self.user, friends__username=self.friend_username).exists() and self.friend_username == "chatbot":
            return

        if message:
            if(len(message) > 500):
                return
            PrivateMessage.objects.create(
                sender=self.user,
                receiver=friend,
                text=message
            )

            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username,
                }
            )
        elif invite:
            random_string = None
            while True:
                random_length = random.randint(1, 8)
                random_string = self.generate_random_string(random_length)
                link = f'/pong_lobby/{random_string}/'
                if(f'game_{random_string}' not in room_manager.rooms):
                    break


            PrivateMessage.objects.create(
                sender=self.user,
                receiver=friend,
                text=link
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': link,
                    'sender': self.user.username,
                }
            )

    def chat_message(self, event):
        sender_nickname = event['sender']
        sender_user = User.objects.filter(username=sender_nickname).first()
        if sender_user in self.user.blocked_users.all():
            return

        self.send(text_data=json.dumps({
            'type': 'chat',
            'sender': event['sender'],
            'message': event['message'],
        }))

    @staticmethod
    def create_room_name(user1, user2):
        return f"private_{min(user1, user2)}_{max(user1, user2)}"


    def generate_random_string(self, length):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(letters_and_digits) for _ in range(length))
        return result_str

