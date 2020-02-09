import logging
import random
from .substructure import Substructure, Node

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

def generate_level(substructures, g_s, g_f, minimum_count=10):

	usage_stats = {}
	original_substructures = {}
	highest_c = 0
	for s in substructures+[g_s,g_f]:
		usage_stats[s.id] = 0
		original_substructures[s.id] = s

	logger.info("Generating level...")
	inserted_list = []

	import copy
	generated_structure = copy.deepcopy(g_s)
	inserted_list.append(g_s)
	logger.info("Initial structure generated! \n{}". format(generated_structure.pretty_print()))

	available_substitutions = generated_structure.get_available_substitutions()
	count_substitutions = 0
	logger.info("Starting substitution process...")
	logger.info("Available subsistutions: {}".format(len(available_substitutions)))

	while len(available_substitutions) > 0:

		selected = False
		while len(available_substitutions) > 0:
			c1, s_id, c2 = random.choice(available_substitutions)
			available_substitutions.remove((c1,s_id, c2))
			if s_id == g_s.id or s_id == g_f.id: continue
			s = original_substructures[s_id]

			#logger.info("Trying to append structure {}".format(s_id))
			#logger.info("\n{}".format(s.pretty_print()))

			adjusted_structure, collides, sim_available_substitutions = generated_structure.expand(s, c1, c2)
			sim_available_substitutions = generated_structure.get_available_substitutions()

			# collides = False
			# level_matrix = {}
			# for n in generated_structure.nodes:
			# 	if (n.r, n.c) not in level_matrix.keys():
			# 		level_matrix[(n.r,n.c)] = n.tile
			# 	else:
			# 		collides = True

			if len(sim_available_substitutions) <= 0 or collides:
				#if len(sim_available_substitutions) <= 0: logger.info("Simulated structure has no available substitutions, trying next...")
				if collides: logger.info("Collision Happened!")
				for n in adjusted_structure.nodes:
					generated_structure.nodes.remove(n)
				for n in adjusted_structure.connecting:
					generated_structure.connecting.remove(n)
				c1.edges[0].properties["combined"] = None
				continue

			else:
				for n in adjusted_structure.nodes:
					if n.c > highest_c:
						highest_c = n.c
				#generated_structure = sim_structure
				selected = True
				usage_stats[s_id] += 1
				inserted_list.append(adjusted_structure)
				break


		if selected == False: continue

		logger.info("Selected substructure: \n{}".format(s.pretty_print()))

		available_substitutions = sim_available_substitutions
		logger.info("Available substitutions: {}".format(len(available_substitutions)))
		logger.info("Substitutions applied so far: {}".format(count_substitutions))
		logger.info("\n{}".format(generated_structure.pretty_print()))

		# if len(inserted_list) > 3:
		# 	for i in range(2):
		# 		logger.info("BACKTRACKING....")
		# 		backtrack(generated_structure, inserted_list)
		# 		logger.info("\n{}".format(generated_structure.pretty_print()))
		# 	import sys
		# 	sys.exit()
		# 	continue


		count_substitutions += 1

		#if count_substitutions >= minimum_count:
		if highest_c >= 202:
			logger.info("Over minimum structure limit. Trying to combine g_f...")
			for connecting in sorted(generated_structure.connecting, key=lambda x: x.c, reverse=True):
				if connecting.edges[0].properties["combined"] == None:
					for s_id, n2 in connecting.edges[0].properties["combinable"]:
						if s_id == g_f.id:
							generated_structure.expand(g_f, connecting, n2)
							return generated_structure, usage_stats, count_substitutions


	return generated_structure, usage_stats, count_substitutions

def instantiate_base_level(id_substructures):
	g_s = Substructure(id_substructures)

	for c in range(3):
		platform = Node(15, c, "X", "Solid", g_s.id)
		g_s.insert_node(platform)

		for r in range(15):
			if r == 14 and c == 1: continue
			air = Node(r, c, "-", "Non-Solid", g_s.id)
			g_s.insert_node(air)

	mario = Node(14, 1, "M", "Solid", g_s.id)
	g_s.insert_node(mario)

	connecting = Node(15, 3, "*", "Connecting", g_s.id)
	connecting.add_edge(connecting, {"direction":"r", "combined":None, "combinable":[]})
	g_s.insert_node(connecting)

	id_substructures += 1

	g_f = Substructure(id_substructures)

	for c in range(1, 3):
		platform = Node(15, c, "X", "Solid", g_f.id)
		g_f.insert_node(platform)

		for r in range(15):
			air = Node(r, c, "-", "Non-Solid", g_f.id)
			g_f.insert_node(air)

	finish = Node(14, 2, "F", "Solid", g_f.id)
	g_f.insert_node(finish)

	connecting = Node(15, 0, "*", "Connecting", g_f.id)
	connecting.add_edge(connecting, {"direction":"l", "combined":None, "combinable":[]})
	g_f.insert_node(connecting)

	return g_s, g_f
