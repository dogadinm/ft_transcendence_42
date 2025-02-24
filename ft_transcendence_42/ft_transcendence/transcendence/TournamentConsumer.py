import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .TournamentGame import tournament_manager
from channels.db import database_sync_to_async
from .models import User

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the tournament ID from the URL route and create a unique group name for the tournament
        self.room_name = self.scope['url_route']['kwargs']['tournament_id']
        self.room_group_name = f"tournament_{self.room_name}"
        self.user = self.scope['user']
        
        # Get or create a tournament room using the tournament manager
        self.room = tournament_manager.get_or_create_room(self.room_name, False)
        
        # Add the current channel to the tournament's group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)       

        # If the user is not already in the tournament or ready list, add them as a spectator
        if self.user not in self.room.all_ready and self.user not in self.room.tournament_users:
            self.room.tournament_users.add(self.user)
            self.room.spectators.append(self.user)
            self.user.tournament_lobby = self.room_name
            await database_sync_to_async(self.user.save)()

        # Accept the WebSocket connection
        await self.accept()
        await self.send_game_state()    
        await self.broadcast_tournament_state()
        
    async def disconnect(self, close_code):
        user = self.user
        room = self.room

        # Remove the user from the spectators and tournament users lists
        lists_to_check = [room.spectators, room.tournament_users]
        for lst in lists_to_check:
            if user in lst:
                lst.remove(user)

        # Update the user's tournament lobby status in the database
        await database_sync_to_async(
            lambda: User.objects.filter(id=self.user.id).update(tournament_lobby=None)
        )()
        user.tournament_lobby = None
        await database_sync_to_async(user.save)()
        
        # If no users are left in the tournament, remove the room
        if not room.tournament_users:
            tournament_manager.remove_room(self.room_name)

        # Remove the channel from the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.broadcast_tournament_state()
        

    async def receive(self, text_data):
        # If the tournament has a champion, send an error message
        if self.room.champion:
            await self.send(text_data=json.dumps({'error': 'Tournament finished.'}))
            return
        
        # If the game is full and the user is not part of it, send an error message
        if len(self.room.all_ready) == 4 and self.user not in self.room.all_ready:
            await self.send(text_data=json.dumps({'error': 'You are not part of the current game.'}))
            return
        
        # Parse the incoming JSON data
        data = json.loads(text_data)
        action = data.get('action')
        
        # Handle the 'ready' action
        if action == 'ready':
            self.room.add_ready_player(self.user)
            self.room.spectators.remove(self.user)
            
            # If 4 players are ready, assign roles and start the tournament
            if len(self.room.all_ready) == 4:
                self.room.assign_role()
                await self.send_game_state()
                if not self.room.is_tournament_running:
                    self.room.is_tournament_running = True
                    asyncio.create_task(self.room.start_tournament(self.send_update, self.broadcast_tournament_state, self.close_tournament, self.send_notification, self.start_countdown))
            await self.broadcast_tournament_state()

        # Handle the 'ready_game' action
        elif action == 'ready_game':
            if self.user == self.room.current_players['left']:
                self.room.ready['left'] = True
            elif self.user == self.room.current_players['right']:
                self.room.ready['right'] = True
            await self.broadcast_tournament_state()
        
        # Handle the 'move' and 'stop' actions for paddle movement
        elif action in ["move", "stop"]:
            direction = data.get('direction')
            if action == "move":
                await self.handle_move(direction)
            elif action == "stop":
                await self.handle_stop(direction)

    async def handle_move(self, direction):
        move_dir = -1 if direction == 'up' else 1
        player_side = None
        for side, player in self.room.current_players.items():
            if player == self.user:
                player_side = side
                break
        if player_side:
            self.room.paddles[player_side]['direction'] = move_dir

    async def handle_stop(self, direction):
        if direction in ['up', 'down']:
            player_side = None
            for side, player in self.room.current_players.items():
                if player == self.user:
                    player_side = side
                    break
            if player_side:
                self.room.paddles[player_side]['direction'] = 0

    # Start the countdown before the game begins
    async def start_countdown(self):
        await self.countdown_and_start_game()

    async def countdown_and_start_game(self):
        for seconds in range(5, 0, -1):
            await self.send_group_message('timer_start', seconds)
            await self.broadcast_tournament_state()
            await asyncio.sleep(1)

    # Send a message to the entire group
    async def send_group_message(self, message_type, state):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'state': state,
            },
        )   
        
    async def broadcast_tournament_state(self):
        state = {
            'spectators': [user.tournament_nickname for user in self.room.spectators],
            'round_winners': [user.tournament_nickname for user in self.room.round_winners],
            'current_players': {
                'left': self.room.current_players['left'].tournament_nickname if self.room.current_players['left'] else None,
                'right': self.room.current_players['right'].tournament_nickname if self.room.current_players['right'] else None,
            },
            'ready': {'left': self.room.ready['left'],'right': self.room.ready['right'],},
            'all_ready': [user.tournament_nickname for user in self.room.all_ready],
            'champion': self.room.champion,
        }
        await self.send_group_message("tournament_state", state)

    async def send_notification(self):
        state = {   
                'massage': f"""Tournament {self.room_name}: {self.room.current_players['left'].tournament_nickname if self.room.current_players['left'] else None} vs {self.room.current_players['right'].tournament_nickname if self.room.current_players['right'] else None}""",
            }
        await self.send_group_message("notification", state)

    async def close_tournament(self):
        await self.send_group_message("close_connection", None)

    async def send_update(self, game_state):
        await self.send_group_message("game_update", game_state)

    async def send_game_state(self):
        await self.send_group_message("game_update", self.room.get_game_state())

 
    # Handles
    async def timer_start(self, event):
        await self.send(text_data=json.dumps({'type': 'timer_start','state': event['state'],}))

    async def notification(self, event):
        await self.send(text_data=json.dumps({'type': 'notification', 'state':event['state']}))
    
    async def tournament_state(self, event):
        await self.send(text_data=json.dumps({'type': 'tournament_state', 'state':event['state']}))

    async def close_connection(self, event=None):
        await self.close()

    async def game_update(self, event):
        await self.send(text_data=json.dumps({'type': 'game_update', 'state': event['state']}))

    async def tournament_end(self, event):
        await self.send(text_data=json.dumps({'type': 'tournament_end', 'state': event['champion']}))