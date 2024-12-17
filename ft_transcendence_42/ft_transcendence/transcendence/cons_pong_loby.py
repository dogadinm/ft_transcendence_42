import json
import threading
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class PongLoby(WebsocketConsumer):
    players = []  # List for two players
    spectators = []  # List for spectators
    ready_players = set()
    timer = None  # Timer reference

    def connect(self):
        self.room_loby = self.scope['url_route']['kwargs']['room_loby']
        self.room_loby_name = f'game_{self.room_loby}'
        self.user = self.scope['user']
        self.username = self.user.username

        self.accept()

        # Add user to the room
        async_to_sync(self.channel_layer.group_add)(
            self.room_loby_name, self.channel_name
        )

        # Determine the role
        if len(self.players) < 2:
            self.players.append(self.username)
            role = "player"
        else:
            self.spectators.append(self.username)
            role = "spectator"

        # Notify all users
        self.broadcast_lobby_state()

        # Send role to the user
        self.send(text_data=json.dumps({
            'type': 'connection',
            'role': role,
            'username': self.username,
        }))

    def disconnect(self, close_code):
        # Remove the user
        if self.username in self.players:
            self.players.remove(self.username)
            self.ready_players.discard(self.username)
        elif self.username in self.spectators:
            self.spectators.remove(self.username)

        # Cancel timer if someone leaves
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            self.timer = None

        # Update lobby state
        async_to_sync(self.channel_layer.group_discard)(
            self.room_loby_name, self.channel_name
        )
        self.broadcast_lobby_state()

    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        # Handle 'ready' signal
        if action == "ready":
            self.ready_players.add(self.username)
            self.broadcast_lobby_state()

            # Start timer if both players are ready
            if len(self.ready_players) == 2 and not self.timer:
                self.start_timer()

    def start_timer(self):
        countdown_seconds = 5  # Timer for 5 seconds

        def timer_complete():
            self.timer = None
            self.start_game()

        # Notify clients that timer is starting
        async_to_sync(self.channel_layer.group_send)(
            self.room_loby_name, {
                'type': 'timer_start',
                'countdown': countdown_seconds
            }
        )

        # Start a timer on the server
        self.timer = threading.Timer(countdown_seconds, timer_complete)
        self.timer.start()

    def broadcast_lobby_state(self):
        # Send updated lobby state to all users
        async_to_sync(self.channel_layer.group_send)(
            self.room_loby_name, {
                'type': 'lobby_state',
                'players': self.players,
                'spectators': self.spectators,
                'ready_players': list(self.ready_players),
            }
        )

    def lobby_state(self, event):
        # Send the lobby state to the client
        self.send(text_data=json.dumps({
            'type': 'lobby_state',
            'players': event['players'],
            'spectators': event['spectators'],
            'ready_players': event['ready_players'],
        }))

    def timer_start(self, event):
        # Notify clients about the timer countdown
        self.send(text_data=json.dumps({
            'type': 'timer_start',
            'countdown': event['countdown'],
        }))

    def start_game(self):
        # Notify all users to redirect to the game room
        async_to_sync(self.channel_layer.group_send)(
            self.room_loby_name, {
                'type': 'game_start',
                'room': self.room_loby
            }
        )

    def game_start(self, event):
        # Send game start event to clients
        self.send(text_data=json.dumps({
            'type': 'game_start',
            'room': event['room']
        }))
