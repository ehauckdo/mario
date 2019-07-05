import random, sys
from mapMatrix import *


# check if all characters on a string (up to the
# lengthᵗʰ character) are terminals i.e. lower case
def isAllTerminals(string, length):
	for i in range(len(string)):
		if string[i].istitle():
			return False
		if i == length-1:
			return True
	return True

# given the matrix of a map and a grammar string
# parse the string and insert elements into the map
def parseGrammarString(mapp, grammar):
	
	def addPadding(mapp, start_x):
		y = len(mapp)-1
		for x in range(start_x, start_x+3):
			mapp[len(mapp)-1][x] = "X"

	def addGround(mapp, start_x, length=15):
		for x in range(start_x, start_x+length):
			mapp[-1][x] = "X"

	# add an enemy
	def a(mapp, start_x):
		addGround(mapp, start_x)
		x = random.choice(range(start_x,start_x+12))
		mapp[-2][x] = "g"

	# add a gap
	def b(mapp, start_x):
		addGround(mapp, start_x)
		x_gap_middle = random.choice(range(start_x+4,start_x+8))
		for x in range(x_gap_middle-3, x_gap_middle+3):
			mapp[-1][x] = "-"

	# add a piranha plant
	def c(mapp, start_x):
		addGround(mapp, start_x)
		x = random.choice(range(start_x,start_x+12))
		mapp[-2][x] = mapp[-2][x+1] = "t"
		mapp[-3][x] = mapp[-3][x+1] = "T"

	# add 15 ground blocks for the first section
	for x in range(0, 15):
		mapp[-1][x] = "X"

	x = 15
	for char in grammar:
		mapp[0][x] = "#"

		if char == "a":   a(mapp, x)
		elif char == "b": b(mapp, x)
		elif char == "c": c(mapp, x)
		
		addPadding(mapp, x+12)
		x = x + 15


# generante a grammar string from an initial "S"
def runGrammar(length=9):

	rules = {}

	rules["S"] = {}
	rules["S"]["chance"] = 1
	rules["S"]["rules"] = ["A"]
	rules["S"]["weights"] = [1]

	rules["A"] = {}
	rules["A"]["chance"] = 1
	rules["A"]["rules"] = ["aA", "aB", "B"]
	rules["A"]["weights"] = [0.2, 0.6, 0.2]

	rules["B"] = {}
	rules["B"]["chance"] = 1
	rules["B"]["rules"] = ["bBA", "baCB"]
	rules["B"]["weights"] = [0.3, 0.7]

	rules["C"] = {}
	rules["C"]["chance"] = 1
	rules["C"]["rules"] = ["c", "bc"]
	rules["C"]["weights"] = [0.3, 0.7]   

	rules["D"] = {}
	rules["D"]["chance"] = 1	
	rules["D"]["rules"] = ["bb", "aa", "c"]
	rules["D"]["weights"] = [0.3, 0.5, 0.2]  

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

	while len(grammar_string) < length or isAllTerminals(grammar_string, length) == False:
		previous_string = grammar_string
		#print(grammar_string)
		grammar_string = expand(grammar_string)

	return grammar_string[:length]

map_matrix = initializeMap()

grammar = runGrammar()


parseGrammarString(map_matrix, grammar)
print("Generated string: "+grammar)
printMap(map_matrix)
#saveMap(map_matrix)
