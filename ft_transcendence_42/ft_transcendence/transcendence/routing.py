from django.urls import re_path

from . import consumers
from . import chat_consumer
from . import group_chat_consumer
from . import cons_pong_loby
from . import StatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<channel_nick>[^/]+)/$', group_chat_consumer.ChatGroupConsumer.as_asgi()),
    re_path(r'ws/chat_privet/(?P<friend_username>\w+)/$', chat_consumer.ChatConsumer.as_asgi()),
    re_path(r'ws/doublejack/$', consumers.DoubleJackConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<room_lobby>\w+)/$', cons_pong_loby.PongLobby.as_asgi()),
    re_path(r'ws/chat_group/(?P<channel_nick>\w+)/$', group_chat_consumer.ChatGroupConsumer.as_asgi()),
    re_path('ws/status/', StatusConsumer.StatusConsumer.as_asgi()),
 ]
