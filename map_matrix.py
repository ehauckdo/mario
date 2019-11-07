import logging, inspect
logger = logging.getLogger(__name__)

def initialize_map():
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	matrix = [ [] for i in range(16) ]
	# fill 4x16 with empty tiles
	for y in range(16):
		for x in range(4):
			matrix[y].append("-")

	# fill the ground with block tiles
	for x in range(4):
		matrix[-1][x] = "X"
	
	# set mario initial position
	matrix[-2][1] = "M"

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return matrix	

# reads all maps/sections from a folder and return a dictionary
# in the format of key -> filename, value -> map matrix
def read_folder(folder="sections"):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	import os
	map_files = os.listdir(folder)
	maps = {}

	for m in map_files:
		map = []
		input_file = open(folder+"/"+m, "r")
		for line in input_file:
			map.append([])
			for char in line[:-1]:
				map[-1].append(char)
	
		maps[m] = map

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return maps


def print_map(map):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string)
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))

def save_map(map, map_filename="map.txt"):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	output_file = open(map_filename, "w")
	
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string, sep='', file=output_file)
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	output_file.close()