import asyncio

class RoomGame:
    def __init__(self):
        self.players = {'left': None, 'right': None}
        self.paddles = {'left': {'paddleY': 150}, 'right': {'paddleY': 150}}
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
        self.score = {'player1': 0, 'player2': 0}
        self.game_loop_running = False

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
        # Update the ball position
        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']

        # Check for collision with upper and lower boundaries
        if self.ball['y'] <= 0 or self.ball['y'] >= 400:
            self.ball['dy'] *= -1

        # Checking the ball collision with the rackets
        for side, paddle in self.paddles.items():
            paddle_x = 10 if side == 'left' else 780
            if paddle_x < self.ball['x'] < paddle_x + 10:
                if paddle['paddleY'] < self.ball['y'] < paddle['paddleY'] + 100:
                    self.ball['dx'] *= -1

        # Goal check
        if self.ball['x'] <= 0:
            self.score['player2'] += 1
            self.reset_ball()
        elif self.ball['x'] >= 800:
            self.score['player1'] += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}

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
