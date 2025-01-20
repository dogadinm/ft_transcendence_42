import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import User, Score, Friend, Message, ChatGroup
from django.contrib.auth.hashers import check_password
from .game import room_manager

class ChatGroupConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_nick = self.scope['url_route']['kwargs']['channel_nick']

        self.channel_group_name = f'chat_{self.channel_nick}'
        self.room_lobby_name = f'game_{self.channel_nick}'
        self.user = self.scope['user']
        self.username = self.user.username
        self.chat_message = 'chat_message_' + self.channel_nick
        setattr(self, self.chat_message, self._dynamic_game_update)

        # for room, room_obj in room_manager.rooms.items():
        #     if self.user in room_obj.people:
        #         if room != self.room_lobby_name:
        #             return

        self.chat_group, created = ChatGroup.objects.get_or_create(name=self.channel_nick)

        if created:
            self.chat_group.name = self.channel_nick
            self.chat_group.save()

        if self.user not in self.chat_group.members.all():
            self.chat_group.members.add(self.user)
            async_to_sync(self.channel_layer.group_add)(
                self.channel_group_name, self.channel_name
            )


        self.accept()



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
            'type': self.chat_message,
            'messages': messages_data,
        }))


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'massege':
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
                    'type': self.chat_message,
                    'message': message_data,
                }
            )

    def _dynamic_game_update(self, event):
        message = event['message']

        sender_username = message['sender']
        sender_user = User.objects.filter(username=sender_username).first()
        if sender_user in self.user.blocked_users.all():
            return

        self.send(text_data=json.dumps({
            'type': self.chat_message,
            'message': message,
        }))
