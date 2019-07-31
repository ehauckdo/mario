import random, sys
import map_matrix
import grammar

def read_maps(folder="sections"):
	import os
	map_files = os.listdir(folder)
	maps = {}

	for m in map_files:
		#logging.info("Parsing {}".format(m))
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


sections = read_maps()

def parse_grammar(mapp, grammar_string):

	def add_intro(mapp):
		# add a small 16x4 introduction
		for y in range(16):
			for x in range(4):
				mapp[y].append("-")

		for x in range(4):
			mapp[-1][x] = "X"
		mapp[-2][1] = "M" 

	add_intro(mapp)

	x = 0
	for char in grammar_string:
		step = grammar.apply_rule(mapp, x, char, sections)
		x = x + step


matrix = []
for i in range(16):
	matrix.append([])

grammar_string = "abbcbd"

# parse the string and save the result inside the matrix
parse_grammar(matrix, grammar_string)

print("Generated string: "+grammar_string)
map_matrix.print_map(matrix)
map_matrix.save_map(matrix)
