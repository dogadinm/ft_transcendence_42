import asyncio
import random
from .models import User, Score, MatchHistory
from asgiref.sync import sync_to_async
from django.conf import settings
import csv
import os

class TournamentRoom:
    # Game constants
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 10

    BALL_INITIAL_SPEED = 2.0
    BALL_MAX_Y = 400
    PADDLE_SPEED = 20
    WIN_SCORE = 10
    WIN_POINTS = 10
    LOSS_POINTS = -5

    FIELD_WIDTH = 800
    FIELD_HEIGHT = 400
    

    def __init__(self, tournament_id):
        self.tournament_id = tournament_id
        self.players_queue = [] 
        self.current_players = {'left': None, 'right': None}
        self.spectators = []
        self.paddles = {
            'left': {'paddleY': (TournamentRoom.FIELD_HEIGHT - TournamentRoom.PADDLE_HEIGHT) // 2, 'direction': 0},
            'right': {'paddleY': (TournamentRoom.FIELD_HEIGHT - TournamentRoom.PADDLE_HEIGHT) // 2, 'direction': 0},
        }
        self.ball = {'x': TournamentRoom.FIELD_WIDTH / 2, 'y': TournamentRoom.FIELD_HEIGHT / 2, 'dx': 4, 'dy': 4}
        self.score = {'left': 0, 'right': 0}
        self.ready = {'left': False, 'right': False}
        self.all_ready = set()
        self.speed = TournamentRoom.BALL_INITIAL_SPEED
        self.round_winners = []
        self.round = 0
        self.is_tournament_running = False
        self.champion = None

    def add_ready_player(self, player):
        if len(self.all_ready) < 4:
            self.all_ready.add(player)
            return False
        else:
            return True
        

    def assign_role(self):
        if len(self.all_ready) < 4:
            raise ValueError("Not enough players to start the tournament.")

        ready_list = list(self.all_ready)
        self.players_queue = [player.username for player in ready_list]
        random.shuffle(self.players_queue)
        self.set_next_match()

    def set_next_match(self):
        if len(self.players_queue) > 2:
            self.current_players['left'] = self.players_queue.pop(0)
            self.current_players['right'] = self.players_queue.pop(0)
            self.round = 1
        elif len(self.players_queue) == 2:
            self.current_players['left'] = self.players_queue.pop(0)
            self.current_players['right'] = self.players_queue.pop(0)
            self.round = 2
        elif len(self.round_winners) >= 2:
            self.current_players['left'] = self.round_winners.pop(0)
            self.current_players['right'] = self.round_winners.pop(0)
            self.round = 3


    async def start_tournament(self, send_update, broadcast_tournament_state, close_tournament):
        while len(self.players_queue) + len(self.round_winners) > 1:
            self.is_tournament_running = True
            if not self.current_players['left'] and not self.current_players['right']:
                self.set_next_match()
                await broadcast_tournament_state()
                await send_update(self.get_game_state())

            while not self.ready['left'] or not self.ready['right']:
                await asyncio.sleep(0.1)

            await self.game_loop(send_update)

        if self.round_winners:
            self.champion = self.round_winners[0]
            await broadcast_tournament_state()
        self.is_tournament_running = False
        await close_tournament()


    def check_paddle_collision(self, side, new_x, new_y, paddle_x):
        paddle_y_start = self.paddles[side]['paddleY']
        paddle_y_end = paddle_y_start + TournamentRoom.PADDLE_HEIGHT

        if ((side == 'left' and new_x - TournamentRoom.PADDLE_WIDTH / 2 <= paddle_x + TournamentRoom.PADDLE_WIDTH) or
                (side == 'right' and new_x + TournamentRoom.PADDLE_WIDTH / 2 >= paddle_x - TournamentRoom.PADDLE_WIDTH)):
            if paddle_y_start <= new_y <= paddle_y_end:
                # Adjust ball's vertical direction based on where it hit the paddle
                paddle_center = paddle_y_start + TournamentRoom.PADDLE_HEIGHT / 2
                offset = (new_y - paddle_center) / (TournamentRoom.PADDLE_HEIGHT / 2)  # Normalize offset (-1 to 1)
                self.ball['dy'] += offset * 2  # Adjust vertical speed slightly
                self.ball['dy'] = max(-5, min(5, self.ball['dy']))  # Clamp dy to avoid excessive vertical speed

                return True
        return False
    

    async def game_loop(self, send_update):
        while self.ready['left'] and self.ready['right']:
            self.update_paddles()
            self.update_ball()
            await send_update(self.get_game_state())

            winner = self.end_game()
            if winner:        
                loser = self.current_players['right'] if winner == self.current_players['left'] else self.current_players['left']
                await self.update_scores(winner, loser)
                await self.save_match(winner, loser)
                self.round_winners.append(winner)
                self.reset_game()
                break

            await asyncio.sleep(0.03)

    def update_paddles(self):
        for side, paddle in self.paddles.items():
            paddle['paddleY'] += paddle['direction'] * TournamentRoom.PADDLE_SPEED
            paddle['paddleY'] = max(0, min(TournamentRoom.BALL_MAX_Y - TournamentRoom.PADDLE_HEIGHT, paddle['paddleY']))

    def update_ball(self):
        dx = self.ball['dx'] * self.speed
        dy = self.ball['dy'] * self.speed

        self.ball['x'] += dx
        self.ball['y'] += dy

        if self.ball['y'] <= 0 or self.ball['y'] >= TournamentRoom.FIELD_HEIGHT:
            self.ball['dy'] *= -1

        for side, paddle in self.paddles.items():
            paddle_x = 20 if side == 'left' else TournamentRoom.FIELD_WIDTH - 20
            if self.check_paddle_collision(side, self.ball['x'], self.ball['y'], paddle_x):
                self.ball['dx'] *= -1
                self.speed += 0.1
        
        if self.ball['x'] <= 20:
            self.score['right'] += 1
            self.reset_ball()
        elif self.ball['x'] >= TournamentRoom.FIELD_WIDTH - 20:
            self.score['left'] += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball = {'x': TournamentRoom.FIELD_WIDTH / 2, 'y': TournamentRoom.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.speed = TournamentRoom.BALL_INITIAL_SPEED

    def get_game_state(self):
        return {
            'field': {'width': TournamentRoom.FIELD_WIDTH, 'height': TournamentRoom.FIELD_HEIGHT},
            'paddle': {'width': TournamentRoom.PADDLE_WIDTH, 'height': TournamentRoom.PADDLE_HEIGHT},
            'paddles': self.paddles,
            'ball': self.ball,
            'players': self.current_players,
            'score': self.score,
        }

    def end_game(self):
        if self.score['left'] >= TournamentRoom.WIN_SCORE:
            return self.current_players['left']
        elif self.score['right'] >= TournamentRoom.WIN_SCORE:
            return self.current_players['right']
        return None

    @sync_to_async
    def save_match(self, winner_username, loser_username):
        winner = User.objects.get(username=winner_username)
        loser = User.objects.get(username=loser_username)

        MatchHistory.objects.create(
            winner=winner,
            loser=loser,
            winner_match_score=self.score['left'] if self.current_players['left'] == winner_username else self.score['right'],
            loser_match_score=self.score['right'] if self.current_players['left'] == winner_username else self.score['left'],
            winner_change_score=TournamentRoom.WIN_POINTS,
            loser_change_score=TournamentRoom.LOSS_POINTS
        )

        self.create_csv(winner.username, loser.username)
        # save_blockcahin(winner, loser, f'tournament_{self.tournament_id}_game_{self.round}.csv')
        self.round = 0
        

    @sync_to_async
    def update_scores(self, winner_username, loser_username):
        winner = User.objects.get(username=winner_username)
        loser = User.objects.get(username=loser_username)
        winner_score = Score.objects.get(user=winner)
        loser_score = Score.objects.get(user=loser)
        winner_score.score += TournamentRoom.WIN_POINTS
        loser_score.score += TournamentRoom.LOSS_POINTS

        winner_score.save()
        loser_score.save()

    def reset_game(self):
        self.score = {'left': 0, 'right': 0}
        self.ready = {'left': False, 'right': False}
        self.current_players = {'left': None, 'right': None}
        self.ball = {'x': TournamentRoom.FIELD_WIDTH / 2, 'y': TournamentRoom.FIELD_HEIGHT / 2, 'dx': 4, 'dy': 4}
        self.speed = TournamentRoom.BALL_INITIAL_SPEED
        self.paddles = {
            'left': {'paddleY': (TournamentRoom.FIELD_HEIGHT - TournamentRoom.PADDLE_HEIGHT) // 2, 'direction': 0},
            'right': {'paddleY': (TournamentRoom.FIELD_HEIGHT - TournamentRoom.PADDLE_HEIGHT) // 2, 'direction': 0},
        }


    def create_csv(self, winner, loser):
        tournament_id = self.tournament_id
        game_id = self.round
        game_type = "semi_final" if game_id in [1, 2] else "final" if game_id == 3 else "unknown"

        is_winner_left = winner in self.current_players['left']
        winner_score = self.score['left'] if is_winner_left else self.score['right']
        loser_score = self.score['right'] if is_winner_left else self.score['left']

        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'tournament_{tournament_id}_game_{game_id}.csv')

        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'tournament_id',
                'game_id',
                'game_type',
                'loser_name',
                'loser_score',
                'winner_name',
                'winner_score'
            ])

            writer.writerow([
                tournament_id,
                game_id,
                game_type,
                loser,
                loser_score,
                winner,
                winner_score,
            ])

        return csv_file_path
      
class TournamentRoomManager:
    def __init__(self):
        self.rooms = {}

    def get_or_create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = TournamentRoom(room_name)
        return self.rooms[room_name]

    def remove_room(self, room_name):
        if room_name in self.rooms:
            del self.rooms[room_name]


tournament_manager = TournamentRoomManager()