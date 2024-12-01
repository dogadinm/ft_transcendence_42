import asyncio
import random
from .models import User, Score
from asgiref.sync import sync_to_async
import random
import signal
# import time

# Function to handle the timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Input timed out")

#def value of hand - move to player?
def	evalHand(cards):
	total = 0
	aces = 0
	# Convert cards to their corresponding values
	for card in cards:
		if (card % 13) == 0:  # Ace
			total += 11
			aces += 1
		elif (card % 13) >= 10:  # J, Q, K
			total += 10
		else:
			total += (card % 13) + 1  # Cards 2-10
	# Adjust for Aces if the total exceeds 42
	while total > 42 and aces:
		total -= 10
		aces -= 1
	if (total > 42):
		total *= -1
	return total


# need deck
class Deck:
	def __init__(self) :
		#unicode cards
		self.uni = ["🂡", "🂢", "🂣", "🂤", "🂥", "🂦", "🂧", "🂨", "🂩", "🂪", "🂫", "🂭", "🂮",
				"🂱", "🂲", "🂳", "🂴", "🂵", "🂶", "🂷", "🂸", "🂹", "🂺", "🂻", "🂽", "🂾",
				"🃁", "🃂", "🃃", "🃄", "🃅", "🃆", "🃇", "🃈", "🃉", "🃊", "🃋", "🃍", "🃎",
				"🃑", "🃒", "🃓", "🃔", "🃕", "🃖", "🃗", "🃘", "🃙", "🃚", "🃛", "🃝", "🃞"]
		self.cards = []
		for x in range(52):
			self.cards.append(x)
	def __str__(self):
		str = "("
		for val in self.cards:
			str += self.uni[val] + " "
		str += ")"
		return str
	def drawCard(self) :
		if (len(self.cards) > 0):
			return self.cards.pop(random.randint(0, len(self.cards) - 1))
		else :
			return -1
	
# need player
class Player:
	def __init__(self, name, elo):
		#unicode cards
		self.uni = ["🂡", "🂢", "🂣", "🂤", "🂥", "🂦", "🂧", "🂨", "🂩", "🂪", "🂫", "🂭", "🂮",
				"🂱", "🂲", "🂳", "🂴", "🂵", "🂶", "🂷", "🂸", "🂹", "🂺", "🂻", "🂽", "🂾",
				"🃁", "🃂", "🃃", "🃄", "🃅", "🃆", "🃇", "🃈", "🃉", "🃊", "🃋", "🃍", "🃎",
				"🃑", "🃒", "🃓", "🃔", "🃕", "🃖", "🃗", "🃘", "🃙", "🃚", "🃛", "🃝", "🃞"]
		self.cards = []
		self.name = name
		self.elo = elo
		self.standing = False
		self.wins = 0
	def __str__(self):
		str = "(N: " + self.name + ", "
		str += f'E: {self.elo}, '
		str += f'S: {self.standing}, '
		str += f'W: {self.wins}, H: '
		for val in self.cards:
			str += self.uni[val] + " "
		str += f', {evalHand(self.cards)}'
		str += ")"
		return str

	# get card
	def getCard(self, card):
		self.cards.append(card)
	# empty hand after a game
	def clearHand(self):
		self.cards = []

# need table
class Table:
	def __init__(self) :
		self.deck = Deck()
		self.players = []
		self.games = 0
		self.standing = 0
	#add player
	def addPlayer(self, name, elo):
		self.players.append(Player(name, elo))
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
	#print
	def print(self):
		print()
		print(self.deck)
		print(f'games: {self.games}')
		for player in self.players:
			print(player)
		print()
	#start game
	def	reset(self):
		self.deck = Deck()
		self.standing = 0
		for player in self.players:
			player.clearHand()
			player.standing = False
			player.getCard(self.deck.drawCard())
			player.getCard(self.deck.drawCard())
			player.getCard(self.deck.drawCard())
			player.getCard(self.deck.drawCard())
	#player hit
	def	playerHit(self, n):
		print(f'{n} tries to draw a card')
		if (n >= 0 and n < len(self.players)):
			if (self.players[n].standing == False and evalHand(self.players[n].cards) < 42 and evalHand(self.players[n].cards) >= 0):
				self.players[n].getCard(self.deck.drawCard())
				print(f'{n} draws a card')
				print(self.players[n])
			if (self.players[n].standing == False and evalHand(self.players[n].cards) < 0):
				self.players[n].standing = True
				self.standing += 1
				print(f'{n} is standing')
	#player stand
	def	playerStand(self, n):
		print(f'{n} tries to stand')
		if (n >= 0 and n < len(self.players)):
			if (self.players[n].standing == False):
				self.players[n].standing = True
				self.standing += 1
				print(f'{n} is standing')
	# evaluate hands
	def	eval(self):
		best = -420
		count = 0
		self.games += 1
		for player in self.players:
			if evalHand(player.cards) > best:
				best = evalHand(player.cards)
				count = 1
			elif evalHand(player.cards) == best:
				count += 1
		for player in self.players:
			if evalHand(player.cards) == best:
				player.wins += 1 / count

# # player can take card (until over 20)





# # total arguments
# n = len(sys.argv)

# #need one argument (number of players)
# if n != 2:
# 	quit()
# # Number of players from standard input for testing
# players = int(sys.argv[1])

# # to support more players we need to play with more decks
# if (players < 2 or players > 6):
# 	quit()

# # Set the signal handler for SIGALRM
# signal.signal(signal.SIGALRM, timeout_handler)

# # Set the timeout limit (in seconds)
# timeout_seconds = 30

# #create table to play games
# table = Table()
# i = 0
# print(f'Name player {i} and add elo score')
# for line in sys.stdin:
# 	name, elo = line.rstrip().split()
# 	elo = int(elo)
# 	table.addPlayer(name, elo)
# 	print(f'Player[{i}]: name[{name}] elo[{elo}]')
# 	i += 1
# 	if i >= players:
# 		break
# 	print(f'Name player {i} and add elo score')
# print()
# newDeck = Deck()
# print(newDeck)
# card = newDeck.drawCard()
# print(card)
# print(newDeck)
# table.print()
# table.playerHit(2)
# table.playerHit(2)
# table.playerHit(2)
# table.playerHit(2)
# table.playerHit(2)
# table.playerHit(2)
# table.playerStand(2)
# table.playerHit(6)
# table.playerHit(3)
# table.playerHit(2)
# table.playerStand(3)
# table.playerHit(6)
# table.playerHit(3)
# table.print()
# Function call
# new gane
# - print stuff
# - new game
#	- hit
#	- stand
#	- 30 second wait
# - quit


# print('Type [new] [exit]')
# for line in sys.stdin:
# 	if line.rstrip() == 'new':
# 		signal.alarm(timeout_seconds)
# 		print()
# 		table.reset()
# 		table.print()
# 		print('30 seconds... type "<pindex> h/s"')
# 		try:
# 			for l in sys.stdin:
# 				index, action = l.rstrip().split()
# 				index = int(index)
# 				if action == 's':
# 					table.playerStand(index)
# 				elif action == 'h':
# 					table.playerHit(index)
# 				if (len(table.players) == table.standing):
# 					break
# 		except TimeoutError:
# 			print("You took too long to respond.")
# 		finally:
# 			signal.alarm(0)
# 		table.eval()
# 	elif line.rstrip() == 'exit':
# 		break
# 	table.print()
# 	print()
# 	print('Type [new] [exit]')

class TableGame:
    # def __init__(self):
    #     self.players = {'left': None, 'right': None}
    #     self.paddles = {
    #         'left': {'paddleY': 150, 'direction': 0},  # direction: -1 (up), 1 (down), 0 (stationary)
    #         'right': {'paddleY': 150, 'direction': 0}
    #     }
    #     self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
    #     self.score = {'left': 0, 'right': 0}
    #     self.game_loop_running = False
    #     self.ready = {'left': False, 'right': False}
    #     self.speed = 2.0
    #     self.paddle_speed = 20
    #     self.win_score = 10

    # async def game_loop(self, send_update):
    #     while self.ready['right'] and self.ready['left']:
    #         self.update_paddles()
    #         self.update_ball()
    #         # print(f"Ball position: {self.ball['x']}, {self.ball['y']}")
    #         await send_update(self.get_game_state())
    #         winner = self.end_game()
    #         if winner:
    #             loser = self.players['right'] if winner == self.players['left'] else self.players['left']
    #             await self.update_scores(winner, loser)
    #         await asyncio.sleep(0.03)

    #         if (self.players['left'] == None and self.players['right'] == None):
    #             self.game_loop_running = False

    # def update_paddles(self):
    #     for side, paddle in self.paddles.items():
    #         paddle['paddleY'] += paddle['direction'] * self.paddle_speed
    #         paddle['paddleY'] = max(0, min(300, paddle['paddleY']))

    # def update_ball(self):
    #     # Calculate the new position
    #     new_x = self.ball['x'] + self.ball['dx'] * self.speed
    #     new_y = self.ball['y'] + self.ball['dy'] * self.speed

    #     # Check for collision with upper and lower boundaries
    #     if new_y <= 0 or new_y >= 400:
    #         self.ball['dy'] *= -1
    #         new_y = self.ball['y'] + self.ball['dy'] * self.speed

    #     # Check for collision with paddles
    #     for side, paddle in self.paddles.items():
    #         paddle_x = 20 if side == 'left' else 780
    #         paddle_y_start = paddle['paddleY']
    #         paddle_y_end = paddle['paddleY'] + 100

    #         # Check if ball crosses paddle's X position
    #         if ((self.ball['x'] < paddle_x <= new_x and side == 'right') or
    #             (self.ball['x'] > paddle_x >= new_x and side == 'left')):

    #             # Check if ball is within the paddle's Y range
    #             ball_cross_y = self.ball['y'] + (new_y - self.ball['y']) * \
    #                            ((paddle_x - self.ball['x']) / (new_x - self.ball['x']))

    #             if paddle_y_start <= ball_cross_y <= paddle_y_end:
    #                 self.ball['dx'] *= -1
    #                 self.speed += 0.1
    #                 new_x = self.ball['x'] + self.ball['dx'] * self.speed
    #                 break


    #     # Update the ball's position
    #     self.ball['x'] = new_x
    #     self.ball['y'] = new_y

    #     # Goal check
    #     if self.ball['x'] <= 0:
    #         self.score['right'] += 1
    #         self.reset_ball()
    #     elif self.ball['x'] >= 800:
    #         self.score['left'] += 1
    #         self.reset_ball()

    # def reset_ball(self):
    #     self.ball = {'x': 400, 'y': 200, 'dx': 4, 'dy': 4}
    #     self.ball['dx'] = random.choice([-4, 4])
    #     self.ball['dy'] = random.choice([-3, -2, 2, 3])
    #     self.speed = 2.0

    # def get_game_state(self):
    #     return {
    #         'paddles': self.paddles,
    #         'ball': self.ball,
    #         'score': {
    #             self.players['left']: self.score['left'] if self.players['left'] else 0,
    #             self.players['right']: self.score['right'] if self.players['right'] else 0,
    #         }
    #     }

    # def end_game(self):
    #     if self.score['left'] == self.win_score or self.score['right'] == self.win_score:
    #         self.ready['left'] = False
    #         self.ready['right'] = False
    #         winner = self.players['left'] if self.score['left'] == self.win_score else self.players['right']
    #         return winner
    #     return None

    # @sync_to_async
    # def update_scores(self, winner_username, loser_username):
    #     winner = User.objects.get(username=winner_username)
    #     loser = User.objects.get(username=loser_username)

    #     winner_score = Score.objects.get(user=winner)
    #     loser_score = Score.objects.get(user=loser)
    #     winner_score.score += 10
    #     loser_score.score += 2

    #     winner_score.save()
    #     loser_score.save()
    pass

class DoubleJackTableManager:
    def __init__(self):
        self.tables = {}

    def get_or_create_table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = TableGame()
        return self.tables[table_name]

    def remove_table(self, table_name):
        if table_name in self.tables:
            del self.tables[table_name]


double_jack_table_manager = DoubleJackTableManager()