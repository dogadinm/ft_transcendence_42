#!/usr/bin/python3

import sys
import random

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
	#add player
	def addPlayer(self, name, elo):
		self.players.append(Player(name, elo))
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
		self.players[-1].getCard(self.deck.drawCard())
	#print
	def print(self):
		print(self.deck)
		for player in self.players:
			print(player)
	#start game
	#player hit
	#player stand
	# evaluate hands
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
# Function call
# new gane
# - print stuff
# - new game
#	- hit
#	- stand
#	- 30 second wait
# - quit