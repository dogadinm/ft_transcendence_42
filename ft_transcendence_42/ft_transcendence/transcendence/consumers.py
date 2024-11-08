import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class Calculator(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()   

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        expression = text_data_json['expression']
        try:
            result = eval(expression)
        except Exception as e:
            result = "Invalid Expression"
        self.send(text_data=json.dumps({
            'result': result
        }))


class GameConsumer(AsyncWebsocketConsumer):
    players = {'left': None, 'right': None}
    paddles = {'left': {'paddleY': 150}, 'right': {'paddleY': 150}}
    ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
    score = {'player1': 0, 'player2': 0}
    game_loop_running = False

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Assign player to 'left' or 'right' side if available
        if GameConsumer.players['left'] is None:
            GameConsumer.players['left'] = self.channel_name
        elif GameConsumer.players['right'] is None:
            GameConsumer.players['right'] = self.channel_name

        # Start the game loop if not already running
        if not GameConsumer.game_loop_running:
            GameConsumer.game_loop_running = True
            asyncio.create_task(self.game_loop())

        # Send initial game state to the new player
        await self.send(json.dumps({
            'type': 'game_update',
            'paddles': GameConsumer.paddles,
            'ball': GameConsumer.ball,
            'score': GameConsumer.score,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove the player on disconnect
        if GameConsumer.players['left'] == self.channel_name:
            GameConsumer.players['left'] = None
        elif GameConsumer.players['right'] == self.channel_name:
            GameConsumer.players['right'] = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'paddleY' in data and 'side' in data:
            side = data['side']
            if side in GameConsumer.paddles:
                GameConsumer.paddles[side]['paddleY'] = data['paddleY']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'paddles': GameConsumer.paddles,
                    'ball': GameConsumer.ball,
                    'score': GameConsumer.score,
                }
            )

    async def game_loop(self):
        while True:
            # Update ball position
            GameConsumer.ball['x'] += GameConsumer.ball['dx']
            GameConsumer.ball['y'] += GameConsumer.ball['dy']

            # Ball collision with top/bottom walls
            if GameConsumer.ball['y'] <= 0 or GameConsumer.ball['y'] >= 400:
                GameConsumer.ball['dy'] *= -1

            # Ball collision with paddles
            for side, paddle in GameConsumer.paddles.items():
                paddle_x = 10 if side == 'left' else 780
                if paddle_x < GameConsumer.ball['x'] < paddle_x + 10:
                    if paddle['paddleY'] < GameConsumer.ball['y'] < paddle['paddleY'] + 100:
                        GameConsumer.ball['dx'] *= -1

            # Check for scoring
            if GameConsumer.ball['x'] <= 0:
                GameConsumer.score['player2'] += 1
                await self.reset_ball()
            elif GameConsumer.ball['x'] >= 800:
                GameConsumer.score['player1'] += 1
                await self.reset_ball()

            # Broadcast game state to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'paddles': GameConsumer.paddles,
                    'ball': GameConsumer.ball,
                    'score': GameConsumer.score,
                }
            )
            await asyncio.sleep(0.03)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def reset_ball(self):
        GameConsumer.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
