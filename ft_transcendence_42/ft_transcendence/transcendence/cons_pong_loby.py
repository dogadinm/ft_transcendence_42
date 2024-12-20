import json
import threading
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class PongLoby(WebsocketConsumer):
    players = {"player1": None, "player2": None}  # Slots for two players
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

        # Default role as spectator
        self.spectators.append(self.username)

        # Notify all users
        self.broadcast_lobby_state()

        # Send role to the user
        self.send(text_data=json.dumps({
            'type': 'connection',
            'role': 'spectator',  # Default role
            'username': self.username,
        }))

    def disconnect(self, close_code):
        # Remove the user
        if self.username in self.players.values():
            for role, player in self.players.items():
                if player == self.username:
                    self.players[role] = None
                    self.ready_players.discard(self.username)
                    break
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
        # self.broadcast_lobby_state()

    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "ready":
            # Mark player as ready if they are assigned to a role
            if self.username in self.players.values():
                self.ready_players.add(self.username)
                self.broadcast_lobby_state()

                # Start timer if both players are ready
                if (
                        self.players['player1'] in self.ready_players and
                        self.players['player2'] in self.ready_players and
                        self.players['player1'] is not None and
                        self.players['player2'] is not None
                ):
                    self.start_timer()

        elif action == "assign_role":
            # Handle role assignment
            requested_role = data.get("role")

            # Ensure the same player cannot occupy both roles
            if self.username in self.players.values():
                self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are already assigned to a role.'
                }))
                return

            # Assign role if available
            if requested_role in self.players and not self.players[requested_role]:
                self.players[requested_role] = self.username
                if self.username in self.spectators:
                    self.spectators.remove(self.username)
                self.broadcast_lobby_state()
            else:
                # Notify the user if the role is taken
                self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Role already taken or invalid.'
                }))

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
        lobby_state = {
            'player1': {
                'name': self.players['player1'],
                'ready': self.players['player1'] in self.ready_players if self.players['player1'] else False,
            },
            'player2': {
                'name': self.players['player2'],
                'ready': self.players['player2'] in self.ready_players if self.players['player2'] else False,
            },
            'spectators': self.spectators,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.room_loby_name, {
                'type': 'lobby_state',
                'state': lobby_state,
            }
        )

    def lobby_state(self, event):
        # Send the lobby state to the client
        self.send(text_data=json.dumps({
            'type': 'lobby_state',
            'state': event['state'],
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
