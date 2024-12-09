from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<room_name>\w+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<channel_nick>[^/]+)/$', consumers.ChatGroupConsumer.as_asgi()),
    re_path(r'ws/chat_privet/(?P<friend_username>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #  re_path(r'ws/socket-server/', consumers.ChatConsumer.as_asgi()),   

 ]
