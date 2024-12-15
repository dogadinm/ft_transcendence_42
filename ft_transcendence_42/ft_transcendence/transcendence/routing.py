from django.urls import re_path

from . import consumers
from . import chat_consumer
from . import group_chat_consumer

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<room_name>\w+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<channel_nick>[^/]+)/$', group_chat_consumer.ChatGroupConsumer.as_asgi()),
    re_path(r'ws/chat_privet/(?P<friend_username>\w+)/$', chat_consumer.ChatConsumer.as_asgi()),
    re_path(r'ws/doublejack/$', consumers.DoubleJackConsumer.as_asgi()),
 ]
