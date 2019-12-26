import map_matrix
import logging, inspect

logger = logging.getLogger(__name__)

# return the production rules of the grammar
def get_grammar_rules(type="coins"):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	rules = {}

	if type == "coins":

		rules["S"] = {}
		rules["S"]["chance"] = 1
		rules["S"]["rules"] = ["A"]
		rules["S"]["weights"] = [1]

		rules["A"] = {}
		rules["A"]["chance"] = 1
		rules["A"]["rules"] = ["aB", "bB"]
		rules["A"]["weights"] = [0.5, 0.5]

		rules["B"] = {}
		rules["B"]["chance"] = 1
		rules["B"]["rules"] = ["eC", "fC"]
		rules["B"]["weights"] = [1/2, 1/2]

		rules["C"] = {}
		rules["C"]["chance"] = 1
		rules["C"]["rules"] = ["iD", "jD"]
		rules["C"]["weights"] = [1/2, 1/2]

		rules["D"] = {}
		rules["D"]["chance"] = 1
		rules["D"]["rules"] = ["m", "n"]
		rules["D"]["weights"] = [1/2, 1/2]

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return rules

# receives the production rules of a grammar as a param,
# generante a grammar string from an initial "S"
def generate_string(rules, length=5):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	import random

	def expand(grammar_string):
		new_string = ""
		for c in grammar_string:
			if c in rules.keys() and random.random() < rules[c]["chance"]:
				new_string += random.choices(rules[c]["rules"], 
												rules[c]["weights"])[0]
			else: new_string += c
		return new_string

	def contains_nonterminals(string):
		for i in range(len(string)):
			if string[i].istitle(): return True
			if i == len(string)-1: return False

	grammar_string = "S"

	while len(grammar_string) < length and contains_nonterminals(grammar_string) == True:
		previous_string = grammar_string
		grammar_string = expand(grammar_string)

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return grammar_string[:length]

# receives a string generated from a grammar and a set of
# character -> section map file
# returns a map generated from that string
def string_to_map(grammar_string, rules):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))

	def apply_rule(mapp, start_x, production_rules, rule):
		section = production_rules[rule]
		for y in range(len(section)):
			mapp[y].extend(section[y])

		x_length = len(section[0])
		return x_length

	mapp = map_matrix.initialize_map()

	x = 4
	for char in grammar_string:
		step = apply_rule(mapp, x, rules, char)
		x = x + step

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return mapp

