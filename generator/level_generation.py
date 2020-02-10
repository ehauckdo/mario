import logging
import random
import copy
import sys
from .substructure import Substructure, Node, Connector
from .level import Level

logger = logging.getLogger(__name__)

def backtrack(structures):
	removed_structure = structures.pop()

	for connector in removed_structure.connecting:
		logger.info("Clearing connectors associated with structure {}".format(removed_structure.id))
		if connector.combined != None:
			structure1, c1 = connector.combined
			c1.combined = None
			logger.info("Clearing node {} from structure {}".format(c1.sub_id, structure1.id))
	return structures

def print_level(structures):
	directions = {"r":">", "l":"<", "u":"^", "d":"v"}
	level = Level()
	base_structure = Substructure(-1)

	for s in structures:
		#logger.info("Appending structure...")
		base_structure.nodes.extend(s.nodes)
		base_structure.connecting.extend(s.connecting)
		#logger.info("{}, {}".format(len(base_structure.nodes), len(base_structure.connecting)))
	return base_structure.pretty_print()

def prepare(structure1, c1, structure2, c2):
	"""Prepare structure 2 to to be connected with structure1"""
	horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
	vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

	adjust_column = (c1.c + (horizontal[c1.direction])) - c2.c
	adjust_row = (c1.r + (vertical[c2.direction])) - c2.r

	c1.combined = [structure2, c2]
	c2.combined = [structure1, c1]

	c1.combinable.remove((structure2.id, c2.sub_id))
	c2.combinable.remove((structure1.id, c1.sub_id))

	for n in structure2.nodes+structure2.connecting:
		n.c += adjust_column
		n.r += adjust_row

	for n in reversed(structure2.nodes+structure2.connecting):
		if n.r < 0 or n.r > 15 or n.c < 0:
			try:
				structure2.nodes.remove(n)
			except:
				structure2.connecting.remove(n)
	return structure2

def has_collision(structures):
	#"""Given a list of structures, check if they would collide"""
	level_matrix = {}
	for str in structures:
		for n in str.nodes:
			if (n.r, n.c) not in level_matrix.keys():
				level_matrix[(n.r,n.c)] = n.tile
			else:
				return True
	return False

def get_available_substitutions(structures):
	available =[]
	for str in structures:
		available.extend(str.get_available_substitutions())

	return available

def list_to_dict(structures, g_s, g_f):
	dict_structures = {}
	for s in structures+[g_s,g_f]:
		dict_structures[s.id] = s
	return dict_structures

def generate_level(substructures, g_s, g_f, minimum_count=10):

	original_substructures = list_to_dict(substructures, g_s, g_f)
	usage_stats = dict.fromkeys(original_substructures.keys(), 0)

	count_substitutions = 0
	count_backtrack = 0
	highest_col = 0
	finished = False

	logger.info("Generating level...")
	level = [] # the generating level is a list of structures
	level.append(copy.deepcopy(g_s))
	logger.info("Initial structure generated!\n{}". format(print_level(level)))

	available_substitutions = get_available_substitutions(level)

	logger.info("Starting substitution process...")
	logger.info("Available subsistutions: {}".format(len(available_substitutions)))

	while len(available_substitutions) > 0:

		while True:
			# logger.info("All Available substitutions: ")
			# for str1, c1, str2_id, c2_id in available_substitutions:
			# 	logger.info("Structure {}, connector {}, to Structure {} via connector {}".format(str1.id, c1, str2_id, c2_id))
			while len(available_substitutions) == 0:
				level = backtrack(level)
				available_substitutions = get_available_substitutions(level)
			str1, c1, str2_id, c2_sub_id = random.choice(available_substitutions)
			available_substitutions.remove((str1, c1, str2_id, c2_sub_id))
			if str2_id == g_s.id or str2_id == g_f.id: continue
			str2 =  copy.deepcopy(original_substructures[str2_id])
			c2 = str2.get_connector(c2_sub_id)

			logger.info("Trying to append structure {} using its connector {} via structure {} with connector {}".format(str2_id, c2, str1.id, c1))
			logger.info("\n{}".format(str2.pretty_print()))

			str2 = prepare(str1, c1, str2, c2)
			level.append(str2)

			collides = has_collision(level)
			available_substitutions = get_available_substitutions(level)

			if len(available_substitutions) <= 0 or collides:
				if len(available_substitutions) <= 0: logger.info("Simulated structure has no available substitutions, trying next...")
				if collides: logger.info("Collision Happened!")
				#c1.combined = None # reset state of first connector
				level = backtrack(level)
				available_substitutions = get_available_substitutions(level)
			else:
				usage_stats[str2_id] += 1
				for n in str2.nodes:
					if n.c > highest_col:
						highest_col = n.c
				break

		count_substitutions += 1

		logger.info("Available substitutions: {}".format(len(available_substitutions)))
		logger.info("Substitutions applied so far: {}".format(count_substitutions))
		logger.info("\n{}".format(print_level(level)))

		# if len(level) >= 4:
		# 	while len(level) > 1:
		# 		logger.info("Starting backtracking...")
		# 		level = backtrack(level)
		# 		available_substitutions = get_available_substitutions(level)
		# 		logger.info("Backtrack complete.")
		# 		logger.info("\n{}".format(print_level(level)))
		# 	count_backtrack += 1
		#
		# 	if count_backtrack > 1:
		# 		sys.exit()
		# 	logger.info("Restarting generation...")

		if highest_col >= 202:
			for str1, c1, str2_id, c2_sub_id in available_substitutions:
				if str2_id == g_f.id:
					str2 = copy.deepcopy(g_f)
					c2 = str2.get_connector(c2_sub_id)
					logger.info("Trying to append g_f {} using its connector {} via structure {} with connector {}".format(g_f.id, c2, str1.id, c1))
					str2 = prepare(str1, c1, str2, c2)
					#if not has_collision(level+[str2]):
					level.append(str2)
					logger.info("g_f finished!")
					print("Reached column 202!")
					finished = True
					break
					#else:
					#	logger.info("g_f collided!")

		if finished:
			break

	generated_structure = Substructure(-1)
	for s in level:
		generated_structure.nodes.extend(s.nodes)
	return generated_structure, usage_stats, count_substitutions

def instantiate_base_level(id_substructures):
	g_s = Substructure(id_substructures)
	for c in range(3):
		platform = Node(15, c, "X", "Solid", g_s)
		g_s.nodes.append(platform)

		for r in range(15):
			if r == 14 and c == 1: continue
			air = Node(r, c, "-", "Non-Solid", g_s)
			g_s.nodes.append(air)

	mario = Node(14, 1, "M", "Solid", g_s)
	g_s.nodes.append(mario)

	connector = Connector(15, 3, "r", g_s)
	g_s.append_connector(connector)

	id_substructures += 1
	g_f = Substructure(id_substructures)

	for c in range(1, 3):
		platform = Node(15, c, "X", "Solid", g_f)
		g_f.nodes.append(platform)

		for r in range(15):
			air = Node(r, c, "-", "Non-Solid", g_f)
			g_f.nodes.append(air)

	finish = Node(14, 2, "F", "Solid", g_f)
	g_f.nodes.append(finish)
	connector = Connector(15, 0, "l", g_f)
	g_f.append_connector(connector)

	return g_s, g_f
