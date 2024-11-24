#!/usr/bin/python3

import sys
import random

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
		str = "(" + self.name + ", "
		str += f'{self.elo}, '
		str += f'{self.standing}, '
		str += f'{self.wins}, '
		for val in self.cards:
			str += self.uni[val] + " "
		str += ")"
		return str
	# get card

# need table
class Table:
	def __init__(self) :
		self.deck = Deck()
		self.players = []
		self.games = 0
	#add player
	def addPlayer(self, name, elo):
		self.players.append(Player(name, elo))
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
if (players < 2 or players > 8):
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