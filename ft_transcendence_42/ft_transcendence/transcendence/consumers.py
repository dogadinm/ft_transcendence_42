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


class GameLogic(AsyncWebsocketConsumer):
    players = {'left': None, 'right': None}
    paddles = {'left': {'paddleY': 150}, 'right': {'paddleY': 150}}
    ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
    score = {'player1': 0, 'player2': 0}
    game_loop_running = False

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.role = self.scope['url_route']['kwargs']['role']

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        #Assigning a role
        if self.role == 'player1' and GameLogic.players['left'] is None:
            GameLogic.players['left'] = self.channel_name
        elif self.role == 'player2' and GameLogic.players['right'] is None:
            GameLogic.players['right'] = self.channel_name

        if not GameLogic.game_loop_running:
            GameLogic.game_loop_running = True
            asyncio.create_task(self.game_loop())

        #Sending the initial state of the game
        await self.send(json.dumps({
            'type': 'game_update',
            'paddles': GameLogic.paddles,
            'ball': GameLogic.ball,
            'score': GameLogic.score,
        }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if self.role == 'player1' and GameLogic.players['left'] == self.channel_name:
            GameLogic.players['left'] = None
        elif self.role == 'player2' and GameLogic.players['right'] == self.channel_name:
            GameLogic.players['right'] = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        side = data.get('side')
        if 'paddleY' in data and side in GameLogic.paddles:
            GameLogic.paddles[side]['paddleY'] = data['paddleY']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'paddles': GameLogic.paddles,
                    'ball': GameLogic.ball,
                    'score': GameLogic.score,
                }
            )

    async def game_loop(self):
        while True:
            GameLogic.ball['x'] += GameLogic.ball['dx']
            GameLogic.ball['y'] += GameLogic.ball['dy']

            if GameLogic.ball['y'] <= 0 or GameLogic.ball['y'] >= 400:
                GameLogic.ball['dy'] *= -1

            for side, paddle in GameLogic.paddles.items():
                paddle_x = 10 if side == 'left' else 780
                if paddle_x < GameLogic.ball['x'] < paddle_x + 10:
                    if paddle['paddleY'] < GameLogic.ball['y'] < paddle['paddleY'] + 100:
                        GameLogic.ball['dx'] *= -1

            if GameLogic.ball['x'] <= 0:
                GameLogic.score['player2'] += 1
                await self.reset_ball()
            elif GameLogic.ball['x'] >= 800:
                GameLogic.score['player1'] += 1
                await self.reset_ball()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'paddles': GameLogic.paddles,
                    'ball': GameLogic.ball,
                    'score': GameLogic.score,
                }
            )
            await asyncio.sleep(0.03)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def reset_ball(self):
        GameLogic.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
