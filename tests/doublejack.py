#!/usr/bin/python3

import sys
import random
import signal
import time

# Function to handle the timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Input timed out")

#def value of hand
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

# player can take card (until over 20)





# total arguments
n = len(sys.argv)

#need one argument (number of players)
if n != 2:
	quit()
# Number of players from standard input for testing
players = int(sys.argv[1])

# to support more players we need to play with more decks
if (players < 2 or players > 6):
	quit()

# Set the signal handler for SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)

# Set the timeout limit (in seconds)
timeout_seconds = 30

#create table to play games
table = Table()
i = 0
print(f'Name player {i} and add elo score')
for line in sys.stdin:
	name, elo = line.rstrip().split()
	elo = int(elo)
	table.addPlayer(name, elo)
	print(f'Player[{i}]: name[{name}] elo[{elo}]')
	i += 1
	if i >= players:
		break
	print(f'Name player {i} and add elo score')
print()
newDeck = Deck()
print(newDeck)
card = newDeck.drawCard()
print(card)
print(newDeck)
table.print()
table.playerHit(2)
table.playerHit(2)
table.playerHit(2)
table.playerHit(2)
table.playerHit(2)
table.playerHit(2)
table.playerStand(2)
table.playerHit(6)
table.playerHit(3)
table.playerHit(2)
table.playerStand(3)
table.playerHit(6)
table.playerHit(3)
table.print()
# Function call
# new gane
# - print stuff
# - new game
#	- hit
#	- stand
#	- 30 second wait
# - quit


print('Type [new] [exit]')
for line in sys.stdin:
	if line.rstrip() == 'new':
		signal.alarm(timeout_seconds)
		print()
		table.reset()
		table.print()
		print('30 seconds... type "<pindex> h/s"')
		try:
			for l in sys.stdin:
				index, action = l.rstrip().split()
				index = int(index)
				if action == 's':
					table.playerStand(index)
				elif action == 'h':
					table.playerHit(index)
				if (len(table.players) == table.standing):
					break
		except TimeoutError:
			print("You took too long to respond.")
		finally:
			signal.alarm(0)
		table.eval()
	elif line.rstrip() == 'exit':
		break
	table.print()
	print()
	print('Type [new] [exit]')


# Loop to take multiple lines of input
# try:
#     while True:
#         user_input = input("Enter input (you have 30 seconds): ")
#         print(f"You entered: {user_input}")
# except TimeoutError:
#     print("You took too long to respond. Exiting the program.")