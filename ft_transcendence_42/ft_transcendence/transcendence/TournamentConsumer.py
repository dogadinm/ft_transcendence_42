import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .TournamentGame import tournament_manager

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['tournament_id']
        self.room_group_name = f"tournament_{self.room_name}"
        self.user = self.scope['user']
        self.username = self.scope['user'].username
        self.room = tournament_manager.get_or_create_room(self.room_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)       

        # if self.username not in self.room.players_queue and self.username not in self.room.round_winners:
        #     self.room.spectators.append(self.username)
        if self.username not in self.room.all_ready:
            self.room.spectators.append(self.username)

        await self.accept()
        await self.send_game_state()
        await self.broadcast_tournament_state()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if self.username in self.room.players_queue:
            self.room.players_queue.remove(self.username)
        if self.username in self.room.spectators:
            self.room.spectators.remove(self.username)
        if self.username in self.room.round_winners:
            self.room.round_winners.remove(self.username)

        if not self.room.players_queue and not self.room.spectators and not self.room.round_winners:
            tournament_manager.remove_room(self.room_name)     
        
        print(tournament_manager.rooms)


    async def receive(self, text_data):
        if len(self.room.all_ready) == 4 and self.user not in self.room.all_ready:
            await self.send(text_data=json.dumps({'error': 'You are not part of the current game.'}))
            return
        
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'ready':
            self.room.add_ready_player(self.user)
            self.room.spectators.remove(self.username)
            self.room.players_queue.append(self.username)
            if len(self.room.all_ready) == 4:
                self.room.assign_role()
                await self.send_game_state()
            await self.broadcast_tournament_state()
            


        elif action == 'ready_game':
            if self.username == self.room.current_players['left']:
                self.room.ready['left'] = True
            elif self.username == self.room.current_players['right']:
                self.room.ready['right'] = True
            if self.room.ready['left'] and self.room.ready['right']:
                if not self.room.is_tournament_running:
                    self.room.is_tournament_running = True
                    asyncio.create_task(self.room.start_tournament(self.send_update, self.broadcast_tournament_state, self.close_tournament))
            await self.broadcast_tournament_state()

        elif action in ["move", "stop"]:
            direction = data.get('direction')
            if action == "move":
                await self.handle_move(direction)
            elif action == "stop":
                await self.handle_stop(direction)

    async def broadcast_tournament_state(self):
        state = {
            'type': 'tournament_state',
            'players_queue': self.room.players_queue,
            'spectators': self.room.spectators,
            'round_winners': self.room.round_winners,
            'current_players': self.room.current_players,
            'ready': self.room.ready,
            'all_ready': [user.username for user in self.room.all_ready],
            'champion': self.room.champion,
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'tournament_state',
                'state': state,
            },
        )

    async def tournament_state(self, event):
        state = event['state']
        # print(state)
        await self.send(text_data=json.dumps(state))

    async def handle_move(self, direction):
        # Handle paddle movement
        move_dir = -1 if direction == 'up' else 1
        player_side = None
        for side, player in self.room.current_players.items():
            if player == self.username:
                player_side = side
                break
        if player_side:
            self.room.paddles[player_side]['direction'] = move_dir

    async def handle_stop(self, direction):
        if direction in ['up', 'down']:
            player_side = None
            for side, player in self.room.current_players.items():
                if player == self.username:
                    player_side = side
                    break
            if player_side:
                self.room.paddles[player_side]['direction'] = 0


    async def send_update(self, game_state):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':  'game_update',
                'game_state': game_state,
            }
        )
        
    async def send_game_state(self):
        game_state = self.room.get_game_state()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': game_state,
            },
        )

    async def close_tournament(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'close_connection',
            },
        )

    async def close_connection(self, event=None):
        await self.close()

    async def game_update(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps({'type': 'game_update', 'game_state': game_state}))

    async def tournament_end(self, event):
        champion = event['champion']
        await self.send(text_data=json.dumps({'type': 'tournament_end', 'champion': champion}))