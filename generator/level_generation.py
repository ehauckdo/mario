import logging
import random
import copy
from .substructure import Substructure, Node, Connector
from .level import Level

logger = logging.getLogger(__name__)

def backtrack(structure, inserted_list):
	remove_structure = inserted_list[-1]

	remaining_connecting = []

	for c in remove_structure.connecting:
		logger.info("To be removed: ({}, {})".format(remove_structure.id, c))
		try:
			other_s, other_c = c.edges[0].properties["combined"]
		except:
			logger.info("Failed to remove {}".format(c))
			continue
		remaining_connecting.append(other_c)
		logger.info("Other_c: {}".format(other_c))
		logger.info("combinables: {}".format(other_c.edges[0].properties["combinable"]))
		for i in range(len(other_c.edges[0].properties["combinable"])):
			id, connecting = other_c.edges[0].properties["combinable"][i]
			if connecting.c == other_c.c and connecting.r == other_c.r:
				other_c.edges[0].properties["combinable"].pop(i)
				logger.info("Removed from combinable")
				break
		#other_c.edges[0].properties["combinable"].remove((remove_structure.id, c))
		other_c.edges[0].properties["combined"] = None

	for n in remove_structure.nodes:
		structure.nodes.remove(n)
	for n in remove_structure.connecting:
		structure.connecting.remove(n)

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
	try:
		c2.combinable.remove((structure1.id, c1.sub_id))
	except:
		pass

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

def generate_level(substructures, g_s, g_f, minimum_count=10):
	import sys
	usage_stats = {}
	original_substructures = {}
	highest_c = 0
	for s in substructures+[g_s,g_f]:
		usage_stats[s.id] = 0
		original_substructures[s.id] = s

	logger.info("Generating level...")
	inserted_list = []

	import copy
	generated_structures = []
	generated_structures.append(copy.deepcopy(g_s))
	#generated_structure = copy.deepcopy(g_s)
	#inserted_list.append(g_s)
	logger.info("Initial structure generated! \n{}". format(generated_structures[-1].pretty_print()))

	available_substitutions = get_available_substitutions(generated_structures)
	count_substitutions = 0
	logger.info("Starting substitution process...")
	logger.info("Available subsistutions: {}".format(len(available_substitutions)))

	while len(available_substitutions) > 0:

		selected = False
		while len(available_substitutions) > 0:
			logger.info("All Available substitutions: ")
			for str1, c1, str2_id, c2_id in available_substitutions:
				logger.info("Structure {}, connector {}, to Structure {} via connector {}".format(str1.id, c1, str2_id, c2_id))

			str1, c1, str2_id, c2_sub_id = random.choice(available_substitutions)
			available_substitutions.remove((str1, c1, str2_id, c2_sub_id))
			if str2_id == g_s.id or str2_id == g_f.id: continue
			str2 =  copy.deepcopy(original_substructures[str2_id])
			c2 = str2.get_connector(c2_sub_id)

			logger.info("Trying to append structure {}".format(str2_id))
			logger.info("\n{}".format(str2.pretty_print()))

			logger.info("using connector: {}".format(c2))

			str2 = prepare(str1, c1, str2, c2)
			logger.info("Adjusted structure {}".format(str2_id))
			logger.info("\n{}".format(str2.pretty_print()))

			collides = has_collision(generated_structures+[str2])
			sim_available_substitutions = get_available_substitutions(generated_structures+[str2])

			if len(sim_available_substitutions) <= 0 or collides:
				if len(sim_available_substitutions) <= 0: logger.info("Simulated structure has no available substitutions, trying next...")
				if collides: logger.info("Collision Happened!")
				c1.combined = None # reset state of first connector
			else:
				usage_stats[str2_id] += 1
				for n in str2.nodes:
					if n.c > highest_c:
						highest_c = n.c
				selected = True
				generated_structures.append(str2)
				break

		if selected == False: continue

		count_substitutions += 1

		logger.info("Selected substructure: \n{}".format(str2.pretty_print()))

		available_substitutions = sim_available_substitutions
		logger.info("Available substitutions: {}".format(len(available_substitutions)))
		logger.info("Substitutions applied so far: {}".format(count_substitutions))
		#logger.info("\n{}".format(generated_structure.pretty_print()))
		logger.info("\n{}".format(print_level(generated_structures)))

		if highest_c >= 202:
			for str1, c1, str2_id, c2_sub_id in available_substitutions:
				if str2_id == g_f.id:
					c2 = str2.get_connector(c2_sub_id)
					str2 = prepare(str1, c1, g_f, c2)
					if has_collision(generated_structures+[str2]):
						continue
					else:
						break

	generated_structure = Substructure(-1)
	for s in generated_structures:
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
