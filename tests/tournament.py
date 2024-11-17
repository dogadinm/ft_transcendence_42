#!/usr/bin/python3

import sys

def add_players(depth, players, values):
	for x in range(depth) :
		if (2 * depth - values[2 * x] + 1 > players) :
			values.insert(2 * x + 1, 0)
		else :
			values.insert(2 * x + 1, 2 * depth - values[2 * x] + 1)

def build_brackets(players):
	depth = 1
	values = [1]
	while depth < players:
		add_players(depth, players, values)
		depth *= 2
	print(values)

# total arguments
n = len(sys.argv)

#need one argument (number of players)
if n < 2:
	quit()
# Number of players from standard input for testing
players = int(sys.argv[1])
if players < 2:
	quit()

# Function call
build_brackets(players)

# 1			Winner
# 12		Final
# 1423		Semifinal
# 10452736	Quarter final