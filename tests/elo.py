#!/usr/bin/python3

import math
import sys

# Function to calculate the Probability
def probability(rating1, rating2):
	# Calculate and return the expected score
	return 1.0 / (1 + math.pow(10, (rating1 - rating2) / 400.0))

# Function to calculate Elo rating
# K is a constant.
# outcome determines the outcome: 1 for Player A win, 0 for Player B win, 0.5 for draw.
def elo_rating(Ra, Rb, K, outcome):
	# Calculate the Winning Probability of Player B
	Pb = probability(Ra, Rb)

	# Calculate the Winning Probability of Player A
	Pa = probability(Rb, Ra)

	# Update the Elo Ratings
	Ra = Ra + K * (outcome - Pa)
	Rb = Rb + K * ((1 - outcome) - Pb)

	# Print updated ratings
	print("Updated Ratings:")
	print(f"Ra = {Ra} Rb = {Rb}")

# total arguments
n = len(sys.argv)

#need four arguments for testing
if n < 5:
	quit()
# Current ELO ratings
Ra = int(sys.argv[1])
Rb = int(sys.argv[2])

Sa = int(sys.argv[3])
Sb = int(sys.argv[4])

Score = Sa / (Sa + Sb)
# K is a constant determining how much the scores change after one match
K = 256

# Outcome: 1 for Player A win, 0 for Player B win, 0.5 for draw
# Score (outcome) is based on player's A performance and the total number of games.
#print(Score)
outcome = Score

# Function call
elo_rating(Ra, Rb, K, outcome)
