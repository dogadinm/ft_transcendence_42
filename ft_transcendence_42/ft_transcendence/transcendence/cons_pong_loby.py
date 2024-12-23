import json
import threading
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
from .game import room_manager
import asyncio

class PongLoby(AsyncWebsocketConsumer):
    players = {"left": None, "right": None}  # Slots for two players
    spectators = []  # List for spectators
    ready_players = set()
    timer = None  # Timer reference


    async def connect(self):
        self.room_loby = self.scope['url_route']['kwargs']['room_loby']
        self.room_loby_name = f'game_{self.room_loby}'
        self.user = self.scope['user']
        self.username = self.user.username
        self.role = 'spectator'

        await self.channel_layer.group_add(self.room_loby_name, self.channel_name)
        await self.accept()



        self.room_game = room_manager.get_or_create_room(self.room_loby)

        self.spectators.append(self.username)
        await self.broadcast_lobby_state()

        # Send role to the user
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'role': self.role,
            'username': self.username,
        }))

    async def disconnect(self, close_code):
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

        await self.channel_layer.group_discard(self.room_loby_name, self.channel_name)
        # self.broadcast_lobby_state()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        direction = data.get('direction')

        if action == "ready":
            if self.username in self.players.values():
                self.ready_players.add(self.username)
                await self.broadcast_lobby_state()

                # Start timer if both players are ready
                if (
                        self.players['left'] in self.ready_players and
                        self.players['right'] in self.ready_players and
                        self.players['left'] is not None and
                        self.players['right'] is not None
                ):
                    self.room_game.ready['left'] = True
                    self.room_game.ready['right'] = True


                    if self.room_game.ready['left'] and self.room_game.ready['right']:
                        asyncio.create_task(self.room_game.game_loop(self.send_game_update))

        elif action == "assign_role":
            # Handle role assignment
            self.requested_role = data.get("role")
            self.role = await self.assign_role()

            # Ensure the same player cannot occupy both roles
            if self.username in self.players.values():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are already assigned to a role.'
                }))
                return

            # Assign role if available
            if self.requested_role  in self.players and not self.players[self.requested_role]:
                self.players[self.requested_role ] = self.username
                if self.username in self.spectators:
                    self.spectators.remove(self.username)
                await self.broadcast_lobby_state()
            else:
                # Notify the user if the role is taken
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Role already taken or invalid.'
                }))

        elif action == 'move':
            print(self.role)
            if self.role == 'left':
                self.room_game.paddles['left']['direction'] = -1 if direction == 'up' else 1
            elif self.role == 'right':
                self.room_game.paddles['right']['direction'] = -1 if direction == 'up' else 1
        elif action == 'stop':
            if self.role == 'left' and direction in ['up', 'down']:
                self.room_game.paddles['left']['direction'] = 0
            elif self.role == 'right' and direction in ['up', 'down']:
                self.room_game.paddles['right']['direction'] = 0


    # def start_timer(self):
    #     countdown_seconds = 5  # Timer for 5 seconds
    #
    #     def timer_complete():
    #         self.timer = None
    #         self.start_game()
    #
    #     # Notify clients that timer is starting
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_loby_name, {
    #             'type': 'timer_start',
    #             'countdown': countdown_seconds
    #         }
    #     )
    #
    #     # Start a timer on the server
    #     self.timer = threading.Timer(countdown_seconds, timer_complete)
    #     self.timer.start()

    async def broadcast_lobby_state(self):
        # Send updated lobby state to all users
        lobby_state = {
            'left': {
                'name': self.players['left'],
                'ready': self.players['left'] in self.ready_players if self.players['left'] else False,
            },
            'right': {
                'name': self.players['right'],
                'ready': self.players['right'] in self.ready_players if self.players['right'] else False,
            },
            'spectators': self.spectators,
        }
        await self.channel_layer.group_send(
            self.room_loby_name, {
                'type': 'lobby_state',
                'state': lobby_state,
            }
        )

    async def lobby_state(self, event):
        # Send the lobby state to the client
        await self.send(text_data=json.dumps({
            'type': 'lobby_state',
            'state': event['state'],
        }))

    # async def timer_start(self, event):
    #     # Notify clients about the timer countdown
    #     await self.send(text_data=json.dumps({
    #         'type': 'timer_start',
    #         'countdown': event['countdown'],
    #     }))

    # def start_game(self):
    #     # Notify all users to redirect to the game room
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_loby_name, {
    #             'type': 'game_start',
    #             'room': self.room_loby
    #         }
    #     )

    async def game_start(self, event):
        # Send game start event to clients
        await self.send(text_data=json.dumps({
            'type': 'game_start',
            'room': event['room']
        }))

    async def assign_role(self):
        print('1')
        if self.requested_role  == 'left':
            self.room_game.players['left'] = self.username
            print('2')
            return 'left'
        elif self.requested_role  == 'right':
            self.room_game.players['right'] = self.username
            return 'right'
        return 'spectator'

    async def send_game_update(self, game_state):
        # print("Sending game update:", game_state)
        winner = self.room_game.end_game()
        await self.channel_layer.group_send(
            self.room_loby_name,
            {
                'type': 'game_update',
                'game_state': game_state
            }
        )
        if winner:
            await self.channel_layer.group_send(
                self.room_loby_name,
                {
                    'type': 'game_over',
                    'winner': winner,
                }
            )

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'paddles': event['game_state']['paddles'],
            'ball': event['game_state']['ball'],
            'score': event['game_state']['score']
        }))