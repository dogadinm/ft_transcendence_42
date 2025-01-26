import json
import asyncio
import random
from .game import room_manager
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .TournamentGame import tournament_manager



# class TournamentConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         """Подключение нового клиента."""
#         self.room_name = self.scope['url_route']['kwargs']['tournament_id']
#         self.room_group_name = f"tournament_{self.room_name}"
#         self.user = self.scope['user']
#         # Присоединяемся к группе канала
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         # Добавляем пользователя в список зрителей
#         self.username = self.scope['user'].username
#         self.room = tournament_manager.get_or_create_room(self.room_name)

#         # Добавляем пользователя в очередь, если он новый
#         if self.username not in self.room.players_queue and self.username not in self.room.round_winners:
#             self.room.players_queue.append(self.username)

#         await self.accept()

#         # Отправляем обновленное состояние всем
#         await self.send_game_state()

#     async def disconnect(self, close_code):
#         """Отключение клиента."""
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#         # Удаляем пользователя из комнаты
#         if self.username in self.room.players_queue:
#             self.room.players_queue.remove(self.username)
#         if self.username in self.room.spectators:
#             self.room.spectators.remove(self.username)

#         # Если комната пустая, удаляем её
#         if not self.room.players_queue and not self.room.spectators and not self.room.round_winners:
#             tournament_manager.remove_room(self.room_name)

#     async def receive(self, text_data):
#         """Обработка сообщений от клиента."""
#         data = json.loads(text_data)
#         action = data.get('action')

#         if action == 'ready':
#             self.room.add_ready_player(self.user)
#             if (len(self.room.all_ready) == 4):
#                 self.room.assign_role()

#         elif action == 'ready_game':
#             if self.username == self.room.current_players['left']:
#                 self.room.ready['left'] = True 
#             elif self.username == self.room.current_players['right']:
#                 self.room.ready['right'] = True
#             if self.room.ready['left'] and self.room.ready['right']:
#                 await self.start_game()  

#         elif action in ["move", "stop"]:
#             direction = data.get('direction')
#             if action == "move":
#                 await self.handle_move(direction)
#             elif action == "stop":
#                 await self.handle_stop(direction)

#     async def handle_move(self, direction):
#         # Handle paddle movement
#         move_dir = -1 if direction == 'up' else 1
#         player_side = None
#         for side, player in self.room.current_players.items():
#             if player == self.username:
#                 player_side = side
#                 break
#         if player_side:
#             self.room.paddles[player_side]['direction'] = move_dir

#     async def handle_stop(self, direction):
#         if direction in ['up', 'down']:
#             player_side = None
#             for side, player in self.room.current_players.items():
#                 if player == self.username:
#                     player_side = side
#                     break
#             if player_side:
#                 self.room.paddles[player_side]['direction'] = 0


#     async def start_game(self):
#         """Запустить игру и отправлять обновления."""
#         async def send_update(game_state):
#             """Отправка состояния игры всем в комнате."""
#             # print(game_state)
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'game_update',
#                     'game_state': game_state,
#                 },
#             )
#         await asyncio.sleep(1)
#         await self.room.start_tournament(send_update)

#     async def send_game_state(self):
#         """Отправить текущее состояние игры всем в комнате."""
#         game_state = self.room.get_game_state()
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'game_update',
#                 'game_state': game_state,
#             },
#         )

#     async def game_update(self, event):
#         """Получить обновление состояния игры и отправить его клиенту."""
#         game_state = event['game_state']
#         await self.send(text_data=json.dumps({'type': 'game_update', 'game_state': game_state}))

#     async def tournament_end(self, event):
#         """Сообщить клиенту о завершении турнира."""
#         champion = event['champion']
#         await self.send(text_data=json.dumps({'type': 'tournament_end', 'champion': champion}))


class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['tournament_id']
        self.room_group_name = f"tournament_{self.room_name}"
        self.user = self.scope['user']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        self.username = self.scope['user'].username
        self.room = tournament_manager.get_or_create_room(self.room_name)

        if self.username not in self.room.players_queue and self.username not in self.room.round_winners:
            self.room.players_queue.append(self.username)
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

        if not self.room.players_queue and not self.room.spectators and not self.room.round_winners:
            tournament_manager.remove_room(self.room_name)
        
        await self.broadcast_tournament_state()

    async def receive(self, text_data):
        """Обработка сообщений от клиента."""
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'ready':
            self.room.add_ready_player(self.user)
            if len(self.room.all_ready) == 4:
                # await self.room.start_tournament(self.send_update)
                self.room.assign_role()
            await self.broadcast_tournament_state()

        elif action == 'ready_game':
            if self.username == self.room.current_players['left']:
                self.room.ready['left'] = True
            elif self.username == self.room.current_players['right']:
                self.room.ready['right'] = True
            if self.room.ready['left'] and self.room.ready['right']:
                asyncio.create_task(self.room.start_tournament(self.send_update))

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
        print(state)
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

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            **event['game_state'],
        }))

        
    async def send_game_state(self):
        game_state = self.room.get_game_state()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_state': game_state,
            },
        )

    async def game_update(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps({'type': 'game_update', 'game_state': game_state}))

    async def tournament_end(self, event):
        champion = event['champion']
        await self.send(text_data=json.dumps({'type': 'tournament_end', 'champion': champion}))