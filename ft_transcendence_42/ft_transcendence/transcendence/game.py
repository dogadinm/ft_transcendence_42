import asyncio
import random
from .models import User, Score, MatchHistory
from asgiref.sync import sync_to_async

class RoomGame:
    # Game constants
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 20
    BALL_INITIAL_SPEED = 2.0
    BALL_MAX_Y = 400
    PADDLE_SPEED = 20
    WIN_SCORE = 10
    WIN_POINTS = 10
    LOSS_POINTS = -5
    FIELD_WIDTH = 800
    FIELD_HEIGHT = 400

    def __init__(self):
        # Game state initialization
        self.players = {'left': None, 'right': None}
        self.paddles = {
            'left': {'paddleY': 150, 'direction': 0},  # direction: -1 (up), 1 (down), 0 (stationary)
            'right': {'paddleY': 150, 'direction': 0}
        }
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.score = {'left': 0, 'right': 0}
        self.spectators = []
        self.ready = {'left': False, 'right': False}
        self.speed = RoomGame.BALL_INITIAL_SPEED

    async def game_loop(self, send_update):
        """Main game loop that updates the game state and notifies clients."""
        while self.ready['left'] and self.ready['right']:
            self.update_paddles()
            self.update_ball()
            await send_update(self.get_game_state())

            winner = self.end_game()
            if winner:
                loser = self.players['right'] if winner == self.players['left'] else self.players['left']
                await self.update_scores(winner, loser)
                await self.save_match(winner, loser)
                break  # End the game loop if there's a winner

            await asyncio.sleep(0.03)  # 30ms frame time

    def update_paddles(self):
        """Update paddle positions based on their direction."""
        for side, paddle in self.paddles.items():
            paddle['paddleY'] += paddle['direction'] * RoomGame.PADDLE_SPEED
            paddle['paddleY'] = max(0, min(RoomGame.BALL_MAX_Y - RoomGame.PADDLE_HEIGHT, paddle['paddleY']))

    def update_ball(self):
        """Update ball position and handle collisions with boundaries and paddles."""
        new_x = self.ball['x'] + self.ball['dx'] * self.speed
        new_y = self.ball['y'] + self.ball['dy'] * self.speed

        # Check collision with top and bottom boundaries
        if new_y <= 0 or new_y >= RoomGame.BALL_MAX_Y:
            self.ball['dy'] *= -1

        # Check collision with paddles
        for side, paddle in self.paddles.items():
            paddle_x = 20 if side == 'left' else RoomGame.FIELD_WIDTH - 20
            if self.check_paddle_collision(side, new_x, new_y, paddle_x):
                self.ball['dx'] *= -1
                self.speed += 0.1  # Slightly increase speed after paddle hit
                break

        # Update ball position
        self.ball['x'] = new_x
        self.ball['y'] = new_y

        # Check for goals
        if self.ball['x'] <= 0:
            self.score['right'] += 1
            self.reset_ball()
        elif self.ball['x'] >= RoomGame.FIELD_WIDTH:
            self.score['left'] += 1
            self.reset_ball()

    def check_paddle_collision(self, side, new_x, new_y, paddle_x):
        """Check if the ball collides with the paddle."""
        paddle_y_start = self.paddles[side]['paddleY']
        paddle_y_end = paddle_y_start + RoomGame.PADDLE_HEIGHT

        if ((side == 'left' and new_x <= paddle_x) or (side == 'right' and new_x >= paddle_x)):
            ball_cross_y = self.ball['y'] + (new_y - self.ball['y']) * \
                ((paddle_x - self.ball['x']) / (new_x - self.ball['x']))
            return paddle_y_start <= ball_cross_y <= paddle_y_end
        return False

    def reset_ball(self):
        """Reset the ball to the center with random initial direction."""
        self.ball = {'x': 400, 'y': 200, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.speed = RoomGame.BALL_INITIAL_SPEED

    def get_game_state(self):
        """Retrieve the current game state."""
        return {
            'paddles': self.paddles,
            'ball': self.ball,
            'players': self.players,
            'score': self.score
        }

    def end_game(self):
        """Check if the game has ended and return the winner."""
        if self.score['left'] >= RoomGame.WIN_SCORE:
            return self.players['left']
        elif self.score['right'] >= RoomGame.WIN_SCORE:
            return self.players['right']
        return None

    @sync_to_async
    def save_match(self, winner_username, loser_username):
        """Save match results to the database."""
        winner = User.objects.get(username=winner_username)
        loser = User.objects.get(username=loser_username)
        MatchHistory.objects.create(
            winner=winner,
            loser=loser,
            winner_match_score=self.score['left'] if self.players['left'] == winner_username else self.score['right'],
            loser_match_score=self.score['right'] if self.players['left'] == winner_username else self.score['left'],
            winner_change_score=RoomGame.WIN_POINTS,
            loser_change_score=RoomGame.LOSS_POINTS
        )
        self.reset_game()

    @sync_to_async
    def update_scores(self, winner_username, loser_username):
        """Update player scores after a match."""
        winner = User.objects.get(username=winner_username)
        loser = User.objects.get(username=loser_username)

        winner_score = Score.objects.get(user=winner)
        loser_score = Score.objects.get(user=loser)
        winner_score.score += RoomGame.WIN_POINTS
        loser_score.score += RoomGame.LOSS_POINTS

        winner_score.save()
        loser_score.save()

    def reset_game(self):
        """Reset the game state for a new match."""
        self.score = {'left': 0, 'right': 0}


class RoomManager:
    """Manages game rooms."""
    def __init__(self):
        self.rooms = {}

    def get_or_create_room(self, room_name):
        """Retrieve an existing room or create a new one."""
        if room_name not in self.rooms:
            self.rooms[room_name] = RoomGame()
        return self.rooms[room_name]

    def remove_room(self, room_name):
        """Remove a room from the manager."""
        if room_name in self.rooms:
            del self.rooms[room_name]


# Global instance of RoomManager
room_manager = RoomManager()
