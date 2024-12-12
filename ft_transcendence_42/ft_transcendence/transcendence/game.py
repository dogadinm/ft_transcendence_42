import asyncio
import random
from .models import User, Score
from asgiref.sync import sync_to_async

class RoomGame:
    def __init__(self):
        self.players = {'left': None, 'right': None}
        self.paddles = {
            'left': {'paddleY': 150, 'direction': 0},  # direction: -1 (up), 1 (down), 0 (stationary)
            'right': {'paddleY': 150, 'direction': 0}
        }
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.score = {'left': 0, 'right': 0}
        self.game_loop_running = False
        self.ready = {'left': False, 'right': False}
        self.speed = 2.0
        self.paddle_speed = 20
        self.win_score = 10

    async def game_loop(self, send_update):
        while self.ready['right'] and self.ready['left']:
            self.update_paddles()
            self.update_ball()
            # print(f"Ball position: {self.ball['x']}, {self.ball['y']}")
            await send_update(self.get_game_state())
            winner = self.end_game()
            if winner:
                loser = self.players['right'] if winner == self.players['left'] else self.players['left']
                await self.update_scores(winner, loser)
            await asyncio.sleep(0.03)

            if (self.players['left'] == None and self.players['right'] == None):
                self.game_loop_running = False

    def update_paddles(self):
        for side, paddle in self.paddles.items():
            paddle['paddleY'] += paddle['direction'] * self.paddle_speed
            paddle['paddleY'] = max(0, min(300, paddle['paddleY']))

    def update_ball(self):
        # Calculate the new position
        new_x = self.ball['x'] + self.ball['dx'] * self.speed
        new_y = self.ball['y'] + self.ball['dy'] * self.speed

        # Check for collision with upper and lower boundaries
        if new_y <= 0 or new_y >= 400:
            self.ball['dy'] *= -1
            new_y = self.ball['y'] + self.ball['dy'] * self.speed

        # Check for collision with paddles
        for side, paddle in self.paddles.items():
            paddle_x = 20 if side == 'left' else 780
            paddle_y_start = paddle['paddleY']
            paddle_y_end = paddle['paddleY'] + 100

            # Check if ball crosses paddle's X position
            if ((self.ball['x'] < paddle_x <= new_x and side == 'right') or
                (self.ball['x'] > paddle_x >= new_x and side == 'left')):

                # Check if ball is within the paddle's Y range
                ball_cross_y = self.ball['y'] + (new_y - self.ball['y']) * \
                               ((paddle_x - self.ball['x']) / (new_x - self.ball['x']))

                if paddle_y_start <= ball_cross_y <= paddle_y_end:
                    self.ball['dx'] *= -1
                    self.speed += 0.1
                    new_x = self.ball['x'] + self.ball['dx'] * self.speed
                    break


        # Update the ball's position
        self.ball['x'] = new_x
        self.ball['y'] = new_y

        # Goal check
        if self.ball['x'] <= 0:
            self.score['right'] += 1
            self.reset_ball()
        elif self.ball['x'] >= 800:
            self.score['left'] += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.ball['dx'] = random.choice([-4, 4])
        self.ball['dy'] = random.choice([-3, -2, 2, 3])
        self.speed = 2.0

    def get_game_state(self):
        return {
            'paddles': self.paddles,
            'ball': self.ball,
            'score': {
                self.players['left']: self.score['left'] if self.players['left'] else 0,
                self.players['right']: self.score['right'] if self.players['right'] else 0,
            }
        }

    def end_game(self):
        if self.score['left'] == self.win_score or self.score['right'] == self.win_score:
            self.ready['left'] = False
            self.ready['right'] = False
            winner = self.players['left'] if self.score['left'] == self.win_score else self.players['right']
            return winner
        return None

    @sync_to_async
    def update_scores(self, winner_username, loser_username):
        winner = User.objects.get(username=winner_username)
        loser = User.objects.get(username=loser_username)

        winner_score = Score.objects.get(user=winner)
        loser_score = Score.objects.get(user=loser)
        winner_score.score += 10
        loser_score.score -= 2

        winner_score.save()
        loser_score.save()

class RoomManager:
    def __init__(self):
        self.rooms = {}

    def get_or_create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = RoomGame()
        return self.rooms[room_name]

    def remove_room(self, room_name):
        if room_name in self.rooms:
            del self.rooms[room_name]


room_manager = RoomManager()
