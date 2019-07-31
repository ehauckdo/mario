import random, sys
import map_matrix

# check if all characters on a string (up to the
# length character) are terminals i.e. lower case
def is_only_terminals(string, length):
	for i in range(len(string)):
		if string[i].istitle():
			return False
		if i == length-1:
			return True
	return True

# given the matrix of a map and a grammar string
# parse the string and insert elements into the map
def parse_grammar(mapp, grammar):
	
	def add_padding(mapp, start_x):
		y = len(mapp)-1
		for x in range(start_x, start_x+3):
			mapp[len(mapp)-1][x] = "X"

	def add_ground(mapp, start_x, length=15):
		for x in range(start_x, start_x+length):
			mapp[-1][x] = "X"

	# add an enemy
	def a(mapp, start_x):
		add_ground(mapp, start_x)
		x = random.choice(range(start_x,start_x+12))
		mapp[-2][x] = "g"

	# add a gap
	def b(mapp, start_x):
		add_ground(mapp, start_x)
		x_gap_middle = random.choice(range(start_x+4,start_x+8))
		for x in range(x_gap_middle-3, x_gap_middle+3):
			mapp[-1][x] = "-"

	# add a piranha plant
	def c(mapp, start_x):
		add_ground(mapp, start_x)
		x = random.choice(range(start_x,start_x+12))
		mapp[-2][x] = mapp[-2][x+1] = "t"
		mapp[-3][x] = mapp[-3][x+1] = "T"

	# add a platform with coins
	def d(mapp, start_x):
		add_ground(mapp, start_x)
		x_gap_middle = random.choice(range(start_x+4,start_x+8))
		for x in range(x_gap_middle-3, x_gap_middle+3):
			mapp[-5][x] = "X"
			if x != x_gap_middle-3 and x != x_gap_middle+2:
				mapp[-6][x] = "o"

	# add 15 ground blocks for the first section
	for x in range(0, 15):
		mapp[-1][x] = "X"

	x = 15
	for char in grammar:
		mapp[0][x] = "#"

		if char == "a":   a(mapp, x)
		elif char == "b": b(mapp, x)
		elif char == "c": c(mapp, x)
		elif char == "d": d(mapp, x)
		
		add_padding(mapp, x+12)
		x = x + 15


# generante a grammar string from an initial "S"
def run_grammar(length=9):

	rules = {}

	rules["S"] = {}
	rules["S"]["chance"] = 1
	rules["S"]["rules"] = ["A"]
	rules["S"]["weights"] = [1]

	rules["A"] = {}
	rules["A"]["chance"] = 1
	rules["A"]["rules"] = ["aA", "bA", "cA", "dA"]
	rules["A"]["weights"] = [0.25, 0.25, 0.25, 0.25]

	def expand(grammar_string):
		new_string = ""
		for char in grammar_string:
			if char in rules.keys() and random.random() < rules[char]["chance"]:
				new_string += random.choices(rules[char]["rules"], rules[char]["weights"])[0]
			else:
				new_string += char
		return new_string

	previous_string = None
	grammar_string = "S"

	while len(grammar_string) < length or is_only_terminals(grammar_string, length) == False:
		previous_string = grammar_string
		#print(grammar_string)
		grammar_string = expand(grammar_string)

	return grammar_string[:length]


# initialize an empty matrix for the map
matrix = map_matrix.initialize_map()

# run the hard coded grammar to generate a new string
grammar = run_grammar()

# parse the string and save the result inside the matrix
parse_grammar(matrix, grammar)

print("Generated string: "+grammar)
map_matrix.print_map(matrix)

map_matrix.save_map(matrix)
