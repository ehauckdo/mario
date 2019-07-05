import logging
from statistics import mean

def calculateLeniency(map_matrix):

	enemy_leniency = -1
	powerup_leniency = 1
	cannon_leniency = -0.5
	flower_leniency = -0.5
	gap_leniency = -0.5
	avggap_leniency = -1

	gaps = findGaps(map_matrix)
	enemies = findEnemies(map_matrix)
	powerups = findPowerUps(map_matrix)
	gaps_width = mean(gaps) if len(gaps) > 0 else 0
	cannon = findCannons(map_matrix)
	flower = findFlowerPiranhas(map_matrix)

	logging.info("Enemies: {}, Powerups: {}, Gaps: {}, Cannons: {}, Flowers: {}, Avg Gap:{}"\
		.format(enemies, powerups, len(gaps), cannon, flower, gaps_width))

	score = enemies * enemy_leniency \
		+ cannon * cannon_leniency \
		+ flower * flower_leniency \
		+ len(gaps) * gap_leniency \
		+ gaps_width * avggap_leniency
	logging.info("Score: {}".format(score))

	return score

def enemiesAndPowerUps(map_matrix):
	score = 0
	# "L" gives an extra life, but I guess this is not
	# really an advantage for a bot, is it?
	powerups = ["@", "U"]
	enemies = ["g", "E","y","Y","G","k","K","r"]
	score = 0

	for line in map_matrix:
		for element in line:
			if element in powerups:
				score += 1
			if element in enemies:
				score -= 1
	return score

def findPowerUps(map_matrix):
	powerups = ["@", "U"]
	count = 0
	for line in map_matrix:
		for element in line:
			if element in powerups:
				count += 1
	return count

def findEnemies(map_matrix):
	enemies = ["g", "E","y","Y","G","k","K","r"]
	count = 0
	for line in map_matrix:
		for element in line:
			if element in enemies:
				count += 1
	return count

def findGaps(map_matrix):
	bottom_row = map_matrix[-1]
	gaps = []
	x = 0
	while x < len(bottom_row):
		if bottom_row[x] == "-":
			x_2 = x
			while x_2 < len(bottom_row) and bottom_row[x_2] == "-":
				x_2 +=1
			gaps.append((x_2-x))
			x = x_2
		x += 1
	return gaps

def findCannons(map_matrix):
	count = 0
	y = 0
	y_len = len(map_matrix[0])
	x_len = len(map_matrix)
	while y < y_len:
		asterisk = 0 # whether there is * in the column
		B = 0 		 # how many cannon heads
		x = 0
		while x < x_len:
			if map_matrix[x][y] == "*":
				asterisk = 1
			if map_matrix[x][y] == "B":
				B +=1
			x += 1 
		y += 1
		count += asterisk + B
	return count

def findFlowerPiranhas(map_matrix):
	count = 0
	y = 0
	y_len = len(map_matrix[0])
	x_len = len(map_matrix)
	while y < y_len-1:
		x = 1 #start from 1 block below ceiling
		while x < x_len:
			if map_matrix[x][y] == "T" and map_matrix[x][y+1] =="T" and map_matrix[x-1][y] == "-" and map_matrix[x-1][y+1] == "-":
				count += 1
			x += 1 
		y += 1
	return count