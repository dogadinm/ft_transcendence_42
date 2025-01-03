import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, Message, ChatGroup
from django.contrib.auth.hashers import check_password


class ChatGroupConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_nick = self.scope['url_route']['kwargs']['channel_nick']
        self.channel_group_name = f'game_{self.channel_nick}'
        self.user = self.scope['user']
        self.username = self.user.username

        self.accept()

        self.chat_group = ChatGroup.objects.get(name=self.channel_nick)

        if not (self.user in self.chat_group.members.all() or self.user == self.chat_group.owner):
            passw = self.chat_group.password != ''

            self.send(text_data=json.dumps({
                'type': 'join',
                'messages': 'Join to the chat',
                'password': passw,

            }))
            return

        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name, self.channel_name
        )
        blocked_users = self.user.blocked_users.all()
        messagesql = Message.objects.filter(chat=self.chat_group).exclude(sender__in=blocked_users).order_by("created_at")

        messages_data = [
            {
                "time": message.created_at.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                "sender": message.sender.username,
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
            password = text_data_json.get('password')
            if self.chat_group.password == '':
                self.chat_group.members.add(self.user)
                self.send(text_data=json.dumps({
                    'type': 'right_pass',
                    'messages': 'Joining to the chat',
                }))
            elif check_password(password, self.chat_group.password):
                self.chat_group.members.add(self.user)
                self.send(text_data=json.dumps({
                    'type': 'right_pass',
                    'messages': 'Joining to the chat',
                }))
            else:
                self.send(text_data=json.dumps({
                    'type': 'wrong_pass',
                    'messages': 'Wrong password',
                }))
            return
        elif action == 'leave':
            self.chat_group.members.remove(self.user)
            return
        elif action == 'massege':
            if not (self.user in self.chat_group.members.all() or self.user == self.chat_group.owner):
                return
            message_text = text_data_json.get('message', '').strip()
            if not message_text:
                return

            messagesql = Message.objects.create(chat=self.chat_group, sender=self.user, text=message_text)

            message_data = {
                "time": messagesql.created_at.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3],
                "sender": messagesql.sender.username,
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

        sender_username = message['sender']
        sender_user = User.objects.filter(username=sender_username).first()
        if sender_user in self.user.blocked_users.all():
            return

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))
