from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/livec/$', consumers.Calculator.as_asgi()),
    re_path(r'ws/game/(?P<room_name>\w+)/$', consumers.GameConsumer.as_asgi()),
 ]
