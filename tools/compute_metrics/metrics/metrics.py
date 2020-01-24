from statistics import mean
import logging, inspect
logger = logging.getLogger(__name__)

def calculate_linearity(map_matrix):
	pass

def calculate_leniency(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

	enemy_leniency = -1
	powerup_leniency = 1
	cannon_leniency = -0.5
	flower_leniency = -0.5
	gap_leniency = -0.5
	avggap_leniency = -1

	gaps = find_gaps(map_matrix)
	enemies = find_enemies(map_matrix)
	powerups = find_powerups(map_matrix)
	gaps_width = mean(gaps) if len(gaps) > 0 else 0
	cannon = find_cannons(map_matrix)
	flower = find_flowerpiranhas(map_matrix)

	logging.info("Enemies: {}, Powerups: {}, Gaps: {}, Cannons: {}, Flowers: {}, Avg Gap:{}"\
		.format(enemies, powerups, len(gaps), cannon, flower, gaps_width))

	score = enemies * enemy_leniency \
		+ cannon * cannon_leniency \
		+ flower * flower_leniency \
		+ len(gaps) * gap_leniency \
		+ gaps_width * avggap_leniency
	logging.info("Score: {}".format(score))

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return score

def find_powerups(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

	powerups = ["@", "U"]
	count = 0
	for line in map_matrix:
		for element in line:
			if element in powerups:
				count += 1
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return count

def find_enemies(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

	enemies = ["g", "E","y","Y","G","k","K","r"]
	count = 0
	for line in map_matrix:
		for element in line:
			if element in enemies:
				count += 1
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return count

def find_gaps(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

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
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return gaps

def find_cannons(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

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
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return count

def find_flowerpiranhas(map_matrix):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

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
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return count