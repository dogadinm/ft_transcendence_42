import asyncio
import random
import csv
import os
from asgiref.sync import sync_to_async
from django.conf import settings
from .models import User, Score, MatchHistory, PrivateMessage, Friend 
from . import blockchain

class TournamentRoom:
    # Game constants
    PADDLE_HEIGHT = 100  # Height of the paddle
    PADDLE_WIDTH = 10     # Width of the paddle
    MAX_BALL_SPEED = 15.0 # Maximum speed of the ball
    BALL_INITIAL_SPEED = 9.0  # Initial speed of the ball
    BALL_MAX_Y = 400      # Maximum Y position of the ball
    PADDLE_SPEED = 20     # Speed of the paddle movement
    WIN_SCORE = 1         # Score required to win a game
    WIN_POINTS = 10       # Points awarded to the winner
    LOSS_POINTS = -5      # Points deducted from the loser
    FIELD_WIDTH = 800     # Width of the game field
    FIELD_HEIGHT = 400    # Height of the game field

    def __init__(self, tournament_id):
        self.tournament_id = tournament_id  # Unique ID for the tournament
        self.players_queue = []             # Queue of players waiting to play
        self.tournament_users = set()       # Set of users participating in the tournament
        self.current_players = {'left': None, 'right': None}  # Current players in the game
        self.spectators = []               # List of spectators watching the game
        self.paddles = {                   # Paddle positions and directions
            'left': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0},
            'right': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0},
        }
        self.ball = {'x': self.FIELD_WIDTH / 2, 'y': self.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}  # Ball position and velocity
        self.score = {'left': 0, 'right': 0}  # Current score of the game
        self.ready = {'left': False, 'right': False}  # Players' readiness status
        self.all_ready = set()              # Set of all players who are ready
        self.speed = self.BALL_INITIAL_SPEED  # Current speed of the ball
        self.round_winners = []             # List of winners from each round
        self.round = 0                      # Current round of the tournament
        self.is_tournament_running = False  # Flag to indicate if the tournament is running
        self.champion = None               # The champion of the tournament

    def add_ready_player(self, player):
        """Add a player to the ready set and check if enough players are ready to start"""
        if len(self.all_ready) < 4:
            self.all_ready.add(player)
            return False
        return True

    def assign_role(self):
        """Assign roles to players and shuffle the queue"""
        if len(self.all_ready) < 4:
            raise ValueError("Not enough players to start the tournament.")
        self.players_queue = list(self.all_ready)
        random.shuffle(self.players_queue)
        self.set_next_match()

    def set_next_match(self):
        """Set the next match by assigning players to left and right positions"""
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

    async def start_tournament(self, send_update, broadcast_tournament_state, close_tournament, send_notification, start_countdown):
        """Main loop to run the tournament"""
        while len(self.players_queue) + len(self.round_winners) > 1:
            self.is_tournament_running = True

            if not self.current_players['left'] and not self.current_players['right']:
                self.set_next_match()
                await broadcast_tournament_state()
                await send_update(self.get_game_state())

            await send_notification()
            while not self.ready['left'] or not self.ready['right']:
                await asyncio.sleep(0.1)
            
            await start_countdown()
            await self.game_loop(send_update) 

        if self.round_winners:
            self.champion = self.round_winners[0].tournament_nickname
            await broadcast_tournament_state()
        self.is_tournament_running = False
        await close_tournament()

    async def game_loop(self, send_update):
        """Main game loop that updates the game state."""
        while self.ready['left'] and self.ready['right']:
            self.update_paddles()
            self.update_ball()
            await send_update(self.get_game_state())
            if winner := self.check_winner():  # Check if there's a winner
                await self.finalize_game(winner)  # Finalize the game (update scores, save match)
                self.round_winners.append(winner)  # Add the winner to the round winners list
                break
            await asyncio.sleep(0.03)  # Small delay to control game loop speed

    async def finalize_game(self, winner):
        """Finalize the game by updating scores and saving match history."""
        loser = self.current_players['right'] if winner == self.current_players['left'] else self.current_players['left']
        await self.update_scores(winner, loser)  # Update scores in the database
        await self.save_match(winner, loser)  # Save match details to the database and blockchain

    def update_paddles(self):
        """Update paddle positions based on their movement direction."""
        for side, paddle in self.paddles.items():
            paddle['paddleY'] += paddle['direction'] * self.PADDLE_SPEED
            paddle['paddleY'] = max(0, min(self.BALL_MAX_Y - self.PADDLE_HEIGHT, paddle['paddleY']))
            
    def check_paddle_collision(self, side, new_x, new_y, paddle_x):
        """Check if the ball collides with the paddle."""
        paddle_y_start = self.paddles[side]['paddleY']
        paddle_y_end = paddle_y_start + self.PADDLE_HEIGHT

        if ((side == 'left' and new_x - self.PADDLE_WIDTH / 2 <= paddle_x + self.PADDLE_WIDTH) or
                (side == 'right' and new_x + self.PADDLE_WIDTH / 2 >= paddle_x - self.PADDLE_WIDTH)):
            if paddle_y_start <= new_y <= paddle_y_end:
                paddle_center = paddle_y_start + self.PADDLE_HEIGHT / 2
                offset = (new_y - paddle_center) / (self.PADDLE_HEIGHT / 2)
                self.ball['dy'] += offset * 2
                self.ball['dy'] = max(-5, min(5, self.ball['dy']))
                return True
        return False
    
    def update_ball(self):
        """Update ball position and handle collisions."""
        step_size = 1

        # Normalize ball speed
        self.normalize_ball_speed()

        dx, dy = self.ball['dx'], self.ball['dy']
        steps = int(max(abs(dx), abs(dy)) / step_size) + 1
        step_dx, step_dy = dx / steps, dy / steps

        for _ in range(steps):
            new_x = self.ball['x'] + step_dx
            new_y = self.ball['y'] + step_dy

            # Handle wall collisions
            if new_y <= 0 or new_y >= self.FIELD_HEIGHT:
                self.ball['dy'] *= -1
                step_dy = self.ball['dy'] / steps
                new_y = self.ball['y'] + step_dy  # Update new_y after reflection

            # Handle paddle collisions
            for side, paddle in self.paddles.items():
                paddle_x = 20 if side == 'left' else self.FIELD_WIDTH - 20
                if self.check_paddle_collision(side, new_x, new_y, paddle_x):
                    self.ball['dx'] *= -1
                    self.adjust_ball_speed()
                    step_dx = self.ball['dx'] / steps
                    new_x = self.ball['x'] + step_dx  # Update new_x after reflection
                    break

            # Update ball position
            self.ball['x'], self.ball['y'] = new_x, new_y

            # Check for goals
            if self.ball['x'] <= 35:
                self.score['right'] += 1
                self.reset_ball()
                return
            elif self.ball['x'] >= self.FIELD_WIDTH - 35:
                self.score['left'] += 1
                self.reset_ball()
                return

    def normalize_ball_speed(self):
        """Ensure the ball maintains its speed after collisions."""
        speed = (self.ball['dx'] ** 2 + self.ball['dy'] ** 2) ** 0.5
        if speed:
            self.ball['dx'] = (self.ball['dx'] / speed) * self.speed
            self.ball['dy'] = (self.ball['dy'] / speed) * self.speed

    def adjust_ball_speed(self):
        """Increase ball speed on paddle collision."""
        self.speed = min(self.speed + 0.05, self.MAX_BALL_SPEED)
        self.normalize_ball_speed()

    def reset_ball(self):
        """Reset the ball."""
        self.ball = {'x': self.FIELD_WIDTH / 2, 'y': self.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.speed = self.BALL_INITIAL_SPEED

    def get_game_state(self):
        """Return the current state of the game."""
        return {
            'field': {'width': self.FIELD_WIDTH, 'height': self.FIELD_HEIGHT},
            'paddle': {'width': self.PADDLE_WIDTH, 'height': self.PADDLE_HEIGHT},
            'paddles': self.paddles,
            'ball': self.ball,
            'players': {
                'left': self.current_players['left'].tournament_nickname if self.current_players['left'] else None,
                'right': self.current_players['right'].tournament_nickname if self.current_players['right'] else None,
            },
            'score': self.score,
        }

    def check_winner(self):
        """Check if there is a winner."""
        if self.score['left'] >= self.WIN_SCORE:
            return self.current_players['left']
        elif self.score['right'] >= self.WIN_SCORE:
            return self.current_players['right']
        return None

    @sync_to_async
    def save_match(self, winner, loser):
        """Save the match result to the database and create a CSV file"""
        MatchHistory.objects.create(
            winner=winner,
            loser=loser,
            winner_match_score=self.score['left'] if self.current_players['left'] == winner else self.score['right'],
            loser_match_score=self.score['right'] if self.current_players['left'] == winner else self.score['left'],
            winner_change_score=self.WIN_POINTS,
            loser_change_score=self.LOSS_POINTS
        )

        self.create_csv(winner.tournament_nickname, loser.tournament_nickname)
        blockchain.save_blockchain(winner, loser, f'tournament_{self.tournament_id}_game_{self.round}.csv')
        self.reset_game()

    @sync_to_async
    def update_scores(self, winner, loser):
        """Update the scores of the winner and loser"""
        winner_score = Score.objects.get(user=winner)
        loser_score = Score.objects.get(user=loser)
        winner_score.score += self.WIN_POINTS
        loser_score.score += self.LOSS_POINTS

        winner_score.save()
        loser_score.save()

    def reset_game(self):
        """Reset the game state for a new match."""
        self.round = 0
        self.score = {'left': 0, 'right': 0}
        self.ready = {'left': False, 'right': False}
        self.current_players = {'left': None, 'right': None}
        self.ball = {'x': self.FIELD_WIDTH / 2, 'y': self.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.speed = self.BALL_INITIAL_SPEED
        self.paddles = {
            'left': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0},
            'right': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0},
        }

    def create_csv(self, winner, loser):
        """Create a CSV file to store the match result"""
        game_type = "semi_final" if self.round in [1, 2] else "final" if self.round == 3 else "unknown"
        is_winner_left = winner == self.current_players['left']
        winner_score = self.score['left'] if is_winner_left else self.score['right']
        loser_score = self.score['right'] if is_winner_left else self.score['left']

        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'tournament_{self.tournament_id}_game_{self.round}.csv')

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
                self.tournament_id,
                self.round,
                game_type,
                loser,
                loser_score,
                winner,
                winner_score,
            ])

        return csv_file_path

class TournamentRoomManager:
    def __init__(self):
        self.rooms = {}  # Dictionary to manage all tournament rooms

    def get_or_create_room(self, room_name, views_check):
        # Get or create a tournament room
        if(views_check and room_name not in self.rooms):
            return False
        if room_name not in self.rooms:
            self.rooms[room_name] = TournamentRoom(room_name)
        return self.rooms[room_name]

    def remove_room(self, room_name):
        # Remove a tournament room
        if room_name in self.rooms:
            del self.rooms[room_name]

# Global instance to manage all tournament rooms
tournament_manager = TournamentRoomManager()