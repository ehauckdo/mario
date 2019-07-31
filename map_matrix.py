def initialize_map():
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

		return matrix	

def read_folder(folder="sections"):
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

	return maps


def print_map(map):
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string)

def save_map(map, map_filename="map.txt"):
	output_file = open(map_filename, "w")
	
	for line in map:
		string = ""
		for char in line:
			string += char
		print(string, sep='', file=output_file)
	output_file.close()