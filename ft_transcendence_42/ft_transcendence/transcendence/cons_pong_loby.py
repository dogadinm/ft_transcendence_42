import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .game import room_manager


class PongLobby(AsyncWebsocketConsumer):
    async def connect(self):
        # Initialize room and user context
        self.room_lobby = self.scope['url_route']['kwargs']['room_lobby']
        self.room_lobby_name = f'game_{self.room_lobby}'
        self.user = self.scope['user']
        self.username = self.user.username
        self.role = 'spectator'

        # Add user to WebSocket group and accept connection
        await self.channel_layer.group_add(self.room_lobby_name, self.channel_name)
        await self.accept()

        # Retrieve or create game room
        self.room_game = room_manager.get_or_create_room(self.room_lobby)
        self.room_game.spectators.append(self.username)
        await self.broadcast_lobby_state()

        # Notify user of connection and initial state
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'role': self.role,
            'username': self.username,
        }))
        await self.send_game_update(self.room_game.get_game_state())

    async def disconnect(self, close_code):
        # Handle player or spectator disconnection
        if self.username == self.room_game.players.get('left'):
            self.room_game.players['left'] = None
            self.room_game.ready['left'] = False
        elif self.username == self.room_game.players.get('right'):
            self.room_game.players['right'] = None
            self.room_game.ready['right'] = False
        elif self.username in self.room_game.spectators:
            self.room_game.spectators.remove(self.username)

        # Remove room if no players remain
        if not self.room_game.players['left'] and not self.room_game.players['right']:
            room_manager.remove_room(self.room_game)

        # Update lobby state and remove user from WebSocket group
        await self.channel_layer.group_discard(self.room_lobby_name, self.channel_name)
        await self.broadcast_lobby_state()

    async def receive(self, text_data):
        # Parse incoming data
        data = json.loads(text_data)
        action = data.get("action")
        direction = data.get("direction")

        if action in ["ready", "assign_role"] and (
                not self.room_game.ready['left'] or not self.room_game.ready['right']):
            if action == "ready":
                await self.handle_ready()
            elif action == "assign_role":
                await self.handle_assign_role(data)
        elif action == "leave":
            await self.handle_leave()
        elif action in ["move", "stop"] and self.role in ["left", "right"]:
            if action == "move":
                await self.handle_move(direction)
            elif action == "stop":
                await self.handle_stop(direction)

    async def handle_ready(self):
        # Mark the player as ready and start the game if both players are ready
        if self.username in self.room_game.players.values():
            role = 'left' if self.username == self.room_game.players['left'] else 'right'
            self.room_game.ready[role] = True
            await self.broadcast_lobby_state()

            # Start the game loop if both players are ready
            if self.room_game.ready['left'] and self.room_game.ready['right']:
                asyncio.create_task(self.room_game.game_loop(self.send_game_update))

    async def handle_assign_role(self, data):
        # Prevent assigning multiple roles to the same user
        if self.username in self.room_game.players.values():
            await self.send_error("You are already assigned to a role.")
            return

        requested_role = data.get("role")
        if requested_role in self.room_game.players and not self.room_game.players[requested_role]:
            # Assign the role if available
            self.role = await self.assign_role(requested_role)
            if self.username in self.room_game.spectators:
                self.room_game.spectators.remove(self.username)
            await self.broadcast_lobby_state()
        else:
            await self.send_error("Role already taken or invalid.")

    async def handle_leave(self):
        # Handle player leaving their role
        for role, player in self.room_game.players.items():
            if player == self.username:
                self.room_game.players[role] = None
                self.room_game.ready[role] = False
                self.role = 'spectator'
                if self.username not in self.room_game.spectators:
                    self.room_game.spectators.append(self.username)
                break
        await self.broadcast_lobby_state()

    async def handle_move(self, direction):
        # Handle paddle movement
        move_dir = -1 if direction == 'up' else 1
        self.room_game.paddles[self.role]['direction'] = move_dir

    async def handle_stop(self, direction):
        # Stop paddle movement
        if direction in ['up', 'down']:
            self.room_game.paddles[self.role]['direction'] = 0

    async def assign_role(self, requested_role):
        # Assign role to the user
        self.room_game.players[requested_role] = self.username
        return requested_role

    async def broadcast_lobby_state(self):
        # Notify all users about the updated lobby state
        lobby_state = {
            'left': {
                'name': self.room_game.players['left'],
                'ready': self.room_game.ready['left'],
            },
            'right': {
                'name': self.room_game.players['right'],
                'ready': self.room_game.ready['right'],
            },
            'spectators': self.room_game.spectators,
        }
        await self.channel_layer.group_send(
            self.room_lobby_name, {
                'type': 'lobby_state',
                'state': lobby_state,
            }
        )

    async def send_game_update(self, game_state):
        # Send updated game state to all users
        await self.channel_layer.group_send(
            self.room_lobby_name,
            {
                'type': 'game_update',
                'game_state': game_state,
            }
        )
        winner = self.room_game.end_game()
        if winner:
            await self.channel_layer.group_send(
                self.room_lobby_name,
                {
                    'type': 'game_over',
                    'winner': winner,
                }
            )

    async def send_error(self, message):
        # Send an error message to the client
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
        }))

    # Event handlers for group messages
    async def lobby_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lobby_state',
            'state': event['state'],
        }))

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            **event['game_state'],
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
        }))
        await self.broadcast_lobby_state()
