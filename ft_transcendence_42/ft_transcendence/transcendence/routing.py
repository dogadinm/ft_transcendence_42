from django.urls import re_path
from . import consumers
from . import ChatConsumer
from . import PongConsumer
from . import StatusConsumer
from . import TournamentConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat_privet/(?P<friend_username>[\w\-]+)/$', ChatConsumer.ChatConsumer.as_asgi()),
    re_path(r'ws/doublejack_lobby/(?P<room_lobby>\w+)/$', consumers.DoubleJackConsumer.as_asgi()),
    re_path(r'ws/lobby/(?P<room_lobby>\w+)/$', PongConsumer.PongLobby.as_asgi()),
    re_path(r'ws/tournament/(?P<tournament_id>\w+)/$', TournamentConsumer.TournamentConsumer.as_asgi()),
    re_path('ws/status/', StatusConsumer.StatusConsumer.as_asgi()),
 ]