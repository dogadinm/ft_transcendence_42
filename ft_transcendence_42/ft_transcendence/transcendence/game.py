import asyncio
import random
from .models import User, Score, MatchHistory
from asgiref.sync import sync_to_async


class RoomGame:
    # Game constants
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 10
    MAX_BALL_SPEED = 15.0
    BALL_INITIAL_SPEED = 9.0
    BALL_MAX_Y = 400
    PADDLE_SPEED = 20
    WIN_SCORE = 1
    WIN_POINTS = 10
    LOSS_POINTS = -5
    FIELD_WIDTH = 800
    FIELD_HEIGHT = 400

    def __init__(self):
        # Initialize game state
        self.people = set()
        self.spectators = []
        self.players = {'left': None, 'right': None}
        self.paddles = {
            'left': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0},  # direction: -1 (up), 1 (down), 0 (stationary)
            'right': {'paddleY': (self.FIELD_HEIGHT - self.PADDLE_HEIGHT) // 2, 'direction': 0}
        }
        self.ball = {'x': self.FIELD_WIDTH / 2, 'y': self.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.score = {'left': 0, 'right': 0}
        self.ready = {'left': False, 'right': False}
        self.speed = self.BALL_INITIAL_SPEED
        self.is_running = False

    async def game_loop(self, send_update):
        """Main game loop that updates the game state and notifies clients."""
        while self.ready['left'] and self.ready['right']:
            self.is_running = True
            self.update_paddles()
            self.update_ball()
            await send_update(self.get_game_state())
            if winner := self.check_winner():
                await self.finalize_game(winner)
                self.is_running = False
                break
            await asyncio.sleep(0.03)  # 30ms per frame
        self.is_running = False

    def update_paddles(self):
        """Update paddle positions based on their movement direction."""
        for side in ('left', 'right'):
            self.paddles[side]['paddleY'] = max(0, min(self.FIELD_HEIGHT - self.PADDLE_HEIGHT, self.paddles[side]['paddleY'] + self.paddles[side]['direction'] * self.PADDLE_SPEED))


    def update_ball(self):
        """Update ball position and handle collisions."""
        step_size = 0.5

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
                dy = self.ball['dy']
                step_dy = dy / steps
                new_y = self.ball['y'] + step_dy  # Update new_y after reflection

            # Handle paddle collisions
            for side, paddle in self.paddles.items():
                paddle_x = 20 if side == 'left' else self.FIELD_WIDTH - 20
                if self.check_paddle_collision(side, new_x, new_y, paddle_x):
                    self.ball['dx'] *= -1
                    self.adjust_ball_speed()
                    dx = self.ball['dx']
                    step_dx = dx / steps
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

    def check_paddle_collision(self, side, new_x, new_y, paddle_x):
        """Check if the ball collides with the paddle."""
        paddle_y_start = self.paddles[side]['paddleY']
        paddle_y_end = paddle_y_start + self.PADDLE_HEIGHT

        if ((side == 'left' and new_x - self.PADDLE_WIDTH / 2 <= paddle_x + self.PADDLE_WIDTH) or
                (side == 'right' and new_x + self.PADDLE_WIDTH / 2 >= paddle_x - self.PADDLE_WIDTH)):
            if paddle_y_start <= new_y <= paddle_y_end:
                # Adjust ball's vertical direction based on where it hit the paddle
                paddle_center = paddle_y_start + self.PADDLE_HEIGHT / 2
                offset = (new_y - paddle_center) / (self.PADDLE_HEIGHT / 2)  # Normalize offset (-1 to 1)
                self.ball['dy'] += offset * 2  # Adjust vertical speed slightly
                self.ball['dy'] = max(-5, min(5, self.ball['dy']))  # Clamp dy to avoid excessive vertical speed
                return True
        return False
         
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
        """Reset the ball to the center with random initial direction."""
        self.ball = {'x': self.FIELD_WIDTH / 2, 'y': self.FIELD_HEIGHT / 2, 'dx': random.choice([-4, 4]), 'dy': random.choice([-3, -2, 2, 3])}
        self.speed = self.BALL_INITIAL_SPEED

    def get_game_state(self):
        """Retrieve the current game state."""
        return {
            'field': {'width': self.FIELD_WIDTH, 'height': self.FIELD_HEIGHT},
            'paddle': {'width': self.PADDLE_WIDTH, 'height': self.PADDLE_HEIGHT},
            'paddles': self.paddles,
            'ball': self.ball,
            'players': self.players,
            'score': self.score
        }

    def check_winner(self):
        """Check if there is a winner."""
        if self.score['left'] >= self.WIN_SCORE:
            return self.players['left']
        if self.score['right'] >= self.WIN_SCORE:
            return self.players['right']
        return None

    async def finalize_game(self, winner):
        """Finalize the game by updating scores and saving match history."""
        loser = self.players['right'] if winner == self.players['left'] else self.players['left']
        winner = await sync_to_async(User.objects.get)(username=winner)
        loser = await sync_to_async(User.objects.get)(username=loser)
        await self.update_scores(winner, loser)
        await self.save_match(winner, loser)
        self.is_running = False

    @sync_to_async
    def save_match(self, winner, loser):
        """Save match results to the database."""
        MatchHistory.objects.create(
            winner=winner,
            loser=loser,
            winner_match_score=self.score['left'] if self.players['left'] == winner.username else self.score['right'],
            loser_match_score=self.score['right'] if self.players['left'] == winner.username else self.score['left'],
            winner_change_score=self.WIN_POINTS,
            loser_change_score=self.LOSS_POINTS
        )
        self.reset_game()

    @sync_to_async
    def update_scores(self, winner, loser):
        """Update player scores after a match."""
        winner_score = Score.objects.get(user=winner)
        loser_score = Score.objects.get(user=loser)
        winner_score.score += self.WIN_POINTS
        loser_score.score += self.LOSS_POINTS
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