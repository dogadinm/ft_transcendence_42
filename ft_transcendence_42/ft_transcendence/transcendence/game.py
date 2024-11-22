import asyncio

class RoomGame:
    def __init__(self):
        self.players = {'left': None, 'right': None}
        self.paddles = {'left': {'paddleY': 150}, 'right': {'paddleY': 150}}
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.score = {'player1': 0, 'player2': 0}
        self.game_loop_running = False
        self.speed = 1.0

    async def game_loop(self, send_update):
        #print("Game loop started")
        while self.game_loop_running:
            self.update_ball()
            # print(f"Ball position: {self.ball['x']}, {self.ball['y']}")
            await send_update(self.get_game_state())
            await asyncio.sleep(0.03)
            if (self.players['left'] == None and self.players['right'] == None):
                self.game_loop_running = False

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
            if (
                    (self.ball['x'] < paddle_x <= new_x and side == 'right') or
                    (self.ball['x'] > paddle_x >= new_x and side == 'left')
            ):
                # Check if ball is within the paddle's Y range
                ball_cross_y = self.ball['y'] + (new_y - self.ball['y']) * \
                               ((paddle_x - self.ball['x']) / (new_x - self.ball['x']))

                if paddle_y_start <= ball_cross_y <= paddle_y_end:
                    self.ball['dx'] *= -1
                    self.speed += 0.1
                    new_x = self.ball['x'] + self.ball['dx'] * self.speed
                    break

        # Goal check
        if new_x <= 0:
            self.score['player2'] += 1
            self.reset_ball()
            return
        elif new_x >= 800:
            self.score['player1'] += 1
            self.reset_ball()
            return

        # Update the ball's position
        self.ball['x'] = new_x
        self.ball['y'] = new_y

        # Goal check
        if self.ball['x'] <= 0:
            self.score['player2'] += 1
            self.reset_ball()
        elif self.ball['x'] >= 800:
            self.score['player1'] += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.speed = 1

    def get_game_state(self):
        return {
            'paddles': self.paddles,
            'ball': self.ball,
            'score': self.score,
        }

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
