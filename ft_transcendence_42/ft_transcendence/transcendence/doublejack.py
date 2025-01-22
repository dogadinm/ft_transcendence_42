import asyncio
import json
import random
from enum import Enum
from .models import User, Score, MatchHistory, ScoreDoubleJack
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .elorating import elo_rating
import random
import signal
# import time

# Shared constants
CARD_UNICODE = [
	"\u1F0A1", "\u1F0A2", "\u1F0A3", "\u1F0A4", "\u1F0A5", "\u1F0A6", "\u1F0A7", "\u1F0A8", "\u1F0A9", "\u1F0AA", "\u1F0AB", "\u1F0AD", "\u1F0AE",
	"\u1F0B1", "\u1F0B2", "\u1F0B3", "\u1F0B4", "\u1F0B5", "\u1F0B6", "\u1F0B7", "\u1F0B8", "\u1F0B9", "\u1F0BA", "\u1F0BB", "\u1F0BD", "\u1F0BE",
	"\u1F0C1", "\u1F0C2", "\u1F0C3", "\u1F0C4", "\u1F0C5", "\u1F0C6", "\u1F0C7", "\u1F0C8", "\u1F0C9", "\u1F0CA", "\u1F0CB", "\u1F0CD", "\u1F0CE",
	"\u1F0D1", "\u1F0D2", "\u1F0D3", "\u1F0D4", "\u1F0D5", "\u1F0D6", "\u1F0D7", "\u1F0D8", "\u1F0D9", "\u1F0DA", "\u1F0DB", "\u1F0DD", "\u1F0DE"
]
CARD_IMAGES = [
	"A-S.png", "2-S.png", "3-S.png", "4-S.png", "5-S.png", "6-S.png", "7-S.png", "8-S.png", "9-S.png", "T-S.png", "J-S.png", "Q-S.png", "K-S.png",
	"A-H.png", "2-H.png", "3-H.png", "4-H.png", "5-H.png", "6-H.png", "7-H.png", "8-H.png", "9-H.png", "T-H.png", "J-H.png", "Q-H.png", "K-H.png",
	"A-D.png", "2-D.png", "3-D.png", "4-D.png", "5-D.png", "6-D.png", "7-D.png", "8-D.png", "9-D.png", "T-D.png", "J-D.png", "Q-D.png", "K-D.png",
	"A-C.png", "2-C.png", "3-C.png", "4-C.png", "5-C.png", "6-C.png", "7-C.png", "8-C.png", "9-C.png", "T-C.png", "J-C.png", "Q-C.png", "K-C.png"
]

class GameStatus(Enum):
	NOT_STARTED = 0
	READY = 1
	IN_PROGRESS = 2
	FINISHED = 4
	ENDED = 8

# Function to handle the timeout
def timeout_handler(signum, frame):
	raise TimeoutError("Input timed out")

#def value of hand - move to player?
def evalHand(cards):
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
	def __init__(self):
		self.cards = list(range(52))  # 52 cards

	def __str__(self):
		return "(" + " ".join(CARD_UNICODE[val] for val in self.cards) + ")"

	def drawCard(self):
		if self.cards:
			return self.cards.pop(random.randint(0, len(self.cards) - 1))
		else:
			return -1

# need player
class Player:
	def __init__(self, name, elo):
		self.cards = []
		self.name = name
		self.elo = elo
		self.standing = False
		self.points = 0

	def __str__(self):
		hand_str = " ".join(CARD_UNICODE[val] for val in self.cards)
		return f"(N: {self.name}, E: {self.elo}, S: {self.standing}, W: {self.points}, H: {hand_str}, {evalHand(self.cards)})"

	def getCard(self, card):
		self.cards.append(card)

	def clearHand(self):
		self.cards = []

# need table
class Table:
	def __init__(self):
		self.deck = Deck()
		self.players = []
		self.games = 0
		self.standing = 0
	def addPlayer(self, name, elo):
		player = Player(name, elo)
		for _ in range(4):
			player.getCard(self.deck.drawCard())
		self.players.append(player)
	#print
	def print(self):
		print(self.deck)
		print(f'games: {self.games}')
		for player in self.players:
			print(player)
	def playerName(self, n):
		if (n >= 0 and n < len(self.players)):
			return (self.players[n].name)
		else:
			return "not a player"
	def playerPoints(self, n):
		if (n >= 0 and n < len(self.players)):
			return (self.players[n].points)
		else:
			return "not a player"
	def playerStatus(self, n):
		if (n >= 0 and n < len(self.players)):
			print("STANDING:")
			print(self.players[n].standing)
			return (self.players[n].standing)
		else:
			return "not a player"
	def playerHand(self, n):
		if 0 <= n < len(self.players):
			return "".join(CARD_IMAGES[val] for val in self.players[n].cards)
		else:
			return "not a player"
	def playerScore(self, n):
		if (n >= 0 and n < len(self.players)):
			return evalHand(self.players[n].cards)
		else:
			return "not a player"
	#start game
	def reset(self):
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
	def playerHit(self, n):
		print(f"{n} tries to draw a card")
		if self.players[n].standing == False:
			print(f"Player {n} is not standing.")
		if (n >= 0 and n < len(self.players)):
			if (self.players[n].standing == False and evalHand(self.players[n].cards) < 42 and evalHand(self.players[n].cards) >= 0):
				self.players[n].getCard(self.deck.drawCard())
				print(f'{n} draws a card')
				# print(self.players[n])
			if (self.players[n].standing == False and (evalHand(self.players[n].cards) < 0 or evalHand(self.players[n].cards) == 42)):
				self.players[n].standing = True
				self.standing += 1
				print(f'{n} is standing')
		print('finished')
	#player stand
	def playerStand(self, n):
		print(f'{n} tries to stand')
		if (n >= 0 and n < len(self.players)):
			if (self.players[n].standing == False):
				self.players[n].standing = True
				self.standing += 1
				print(f'{n} is standing')
	def isPlayerStanding(self, n):
		if (n >= 0 and n < len(self.players)):
			return self.players[n].standing
		else:
			return "not a player"
	# evaluate hands
	def eval(self):
		best = -420
		count = 0
		total = 0
		self.games += 1
		print("EVAL")
		for player in self.players:
			if evalHand(player.cards) > best:
				best = evalHand(player.cards)
				count = 1
			elif evalHand(player.cards) == best:
				count += 1
		for player in self.players:
			if evalHand(player.cards) != best:
				player.points -= best - evalHand(player.cards)
				print("loser")
				print(best - evalHand(player.cards))
				total += best - evalHand(player.cards)
		for player in self.players:
			if evalHand(player.cards) == best:
				player.points += total
				print("winner")
				print(total)

class TableGame:
	def __init__(self, consumer, room_name):
		from .consumers import DoubleJackConsumer
		self.table = Table()
		self.status = GameStatus.NOT_STARTED
		self.players = 0
		self.countdown_time = 30  # Start from 30
		self.is_running = False
		self.room_name = room_name
		self.dj_users = ['']
		self.consumer = consumer
	def addPlayer(self, name, elo):
		if name not in self.dj_users:
			self.dj_users.append(name)
		else :
			return self.dj_users.index(name)
		if self.status != GameStatus.IN_PROGRESS:
			self.table.addPlayer(name, elo)
			self.players += 1
		if self.players == 2:
			self.status = GameStatus.READY
		if self.status == GameStatus.READY:
			self.status = GameStatus.IN_PROGRESS
			self._start_countdown_if_needed()
		print(self.status)
		return len(self.table.players)
	async def playerHit(self, n):
		if self.status == GameStatus.IN_PROGRESS:
			print(f"Player {n} triggered HIT")
			self.table.playerHit(n - 1)
			print("Completed playerHit logic in Table.")
			print("Completed playerHit logic in Table.")
			print("Completed playerHit logic in Table.")
			print("Completed playerHit logic in Table.")
			print("Completed playerHit logic in Table.")
			print("Completed playerHit logic in Table.")
			await self._check_game_status()
			print("Completed _check_game_status.")
	async def playerStand(self, n):
		if self.status == GameStatus.IN_PROGRESS:
			self.table.playerStand(n - 1)
			await self._check_game_status()
	def isPlayerStanding(self, n):
		return self.table.isPlayerStanding(n - 1)
	def playerHand(self, n):
		print("status")
		print(self.status)
		if self.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]:
			return self.table.playerHand(n - 1)
		else:
			return "game not in progress"
	def playerStatus(self, n):
		if self.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]:
			return self.table.playerStatus(n - 1)
		else:
			return "game not in progress"
	def playerPoints(self, n):
		if self.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]:
			return self.table.playerPoints(n - 1)
		else:
			return "game not in progress"
	def playerName(self, n):
		return self.table.playerName(n - 1)
	def playerScore(self, n):
		if self.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]:
			return self.table.playerScore(n - 1)
		else:
			return "game not in progress"
	def tableGames(self, n):
		if self.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]:
			return self.table.games
		else:
			return "game not in progress"
	def reset(self):
		if self.status == GameStatus.FINISHED:
			self.table.reset()
			if self.is_running:
				self.task.cancel()
			self.status = GameStatus.IN_PROGRESS
			self.reset_countdown()
			self._start_countdown_if_needed()
	async def _check_game_status(self):
		if len(self.table.players) == self.table.standing:
			self.status = GameStatus.FINISHED
			self.table.eval()
			if self.is_running:
				self.task.cancel()
			if self.table.playerPoints(0) > 99:
				self.status = GameStatus.ENDED
				print("UPDATE1")
				await self.update_scores(self.table.players[0].name, self.table.players[1].name)
				print("UPDATE1b")
			if self.table.playerPoints(1) > 99:
				self.status = GameStatus.ENDED
				print("UPDATE2")
				await self.update_scores(self.table.players[1].name, self.table.players[0].name)
				print("UPDATE2b")
	def _start_countdown_if_needed(self):
		if self.is_running:
			self.task.cancel()  # Cancel the existing task
		self.task = asyncio.create_task(self.start_countdown())
	async def start_countdown(self):
		if self.is_running:  # Prevent starting another countdown
			return
		self.is_running = True
		channel_layer = get_channel_layer()
		print("STARTING COUNTDOWN")
		while self.countdown_time >= 0:
			await channel_layer.group_send(
				f"ws_{self.room_name}",
				{
					"type": "send_countdown",
					"countdown": self.countdown_time,
					"room_name": self.room_name
				}
			)
			await asyncio.sleep(1)
			self.countdown_time -= 1
			print(self.countdown_time)
		self.status = GameStatus.FINISHED
		self.table.eval()
		await channel_layer.group_send(
			f"ws_{self.room_name}",
				{
					'type': 'reset',
					'reset': 'reset'
				}
			)
		await self.consumer.handle_role_and_send_info("#FF00FF", self.consumer.role - 1 if self.consumer.role == 2 else self.consumer.role + 1)
		await channel_layer.group_send(
			f"ws_{self.room_name}",
			{
				"type": "send_countdown",
				"countdown": "Countdown finished!",
				"room_name": self.room_name
			}
		)
		self.is_running = False
	def reset_countdown(self):
		self.countdown_time = 30
		if self.is_running:
			self.task.cancel()
		self.is_running = False
	def get_countdown_time(self):
		return self.countdown_time
	@database_sync_to_async
	def get_scores_for_users(self, winner_username, loser_username):
		print(f"Fetching scores for users: {winner_username}, {loser_username}")
		winner = User.objects.get(username=winner_username)
		loser = User.objects.get(username=loser_username)
		print(f"Fetched users: winner: {winner}, loser: {loser}")

		winner_score = ScoreDoubleJack.objects.get(user=winner)
		loser_score = ScoreDoubleJack.objects.get(user=loser)
		print(f"Fetched scores: winner_score: {winner_score.score}, loser_score: {loser_score.score}")
		return winner_score, loser_score

	@sync_to_async
	def save_scores(self, winner_score, loser_score):
		print(f"Saving scores: winner_score: {winner_score.score}, loser_score: {loser_score.score}")
		winner_score.save()
		loser_score.save()
		print("Scores saved successfully.")

	async def update_scores(self, winner_username, loser_username):
		print("Starting update_scores...")
		winner_score, loser_score = await self.get_scores_for_users(winner_username, loser_username)
		print(f"Updating scores: winner_score (before): {winner_score.score}, loser_score (before): {loser_score.score}")
		# winner_score.score += 10
		# loser_score.score -= 10
		winner_score.score, loser_score.score = elo_rating(winner_score.score, loser_score.score, 32, 1)
		print(f"Updated scores: winner_score (after): {winner_score.score}, loser_score (after): {loser_score.score}")
		await self.save_scores(winner_score, loser_score)
		print(f"Scores updated for winner: {winner_username}, loser: {loser_username}")


class DoubleJackTableManager:
	def __init__(self):
		self.tables = {}

	def get_or_create_table(self, consumer, table_name):
		if table_name not in self.tables:
			print("new table")
			self.tables[table_name] = TableGame(consumer, table_name)
		return self.tables[table_name]

	def remove_table(self, table_name):
		if table_name in self.tables:
			del self.tables[table_name]

double_jack_table_manager = DoubleJackTableManager()
