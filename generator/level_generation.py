import logging
import random
from .substructure import Substructure, Node

logger = logging.getLogger(__name__)

def generate_level(substructures, g_s, g_f, minimum_count=10):

	substructures_used = {}
	substructures_dict = {}
	for s in substructures+[g_s,g_f]:
		substructures_used[s.id] = 0
		substructures_dict[s.id] = s

	logger.info("Generating level...")

	import copy
	generated_structure = copy.deepcopy(g_s)
	logger.info("Initial structure generated! \n{}". format(generated_structure.pretty_print()))

	available_substitutions = generated_structure.get_available_substitutions()
	count_substitutions = 0
	logger.info("Starting substitution process...")

	levels = []
	while len(available_substitutions) > 0:

		selected = False
		while len(available_substitutions) > 0:
			c1, s_id, c2 = random.choice(available_substitutions)
			available_substitutions.remove((c1,s_id, c2))
			if s_id == g_s.id or s_id == g_f.id: continue
			s = substructures_dict[s_id]

			#sim_structure, collides = generated_structure.simulate_expansion(s, c1, c2)
			#sim_available_substitutions = sim_structure.get_available_substitutions()

			adjusted_structure = generated_structure.expand(s, c1, c2)
			sim_available_substitutions = generated_structure.get_available_substitutions()

			map_matrix = [{} for i in range(16)]
			collides = False
			for n in generated_structure.nodes:
				try:
					if map_matrix[n.r][n.c] != None: collides = True
				except:
					map_matrix[n.r][n.c] = n.tile

			if len(sim_available_substitutions) <= 0 or collides:
				#if len(sim_available_substitutions) <= 0: logger.info("Simulated structure has no available substitutions, trying next...")
				#if collides: logger.info("Collision Happened!")
				for n in adjusted_structure.nodes:
					generated_structure.nodes.remove(n)
				for n in adjusted_structure.connecting:
					generated_structure.connecting.remove(n)
				c1.edges[0].properties["combined"] = None
				continue

			# if collides or len(sim_available_substitutions) <= 0:
			# 	# logger.info("Simulated structure has connecting <= 0 or collides, trying next...")
			# 	logger.info("Simulated structure collides, trying next...")
			# 	continue
			else:

				#generated_structure = sim_structure
				selected = True
				substructures_used[s_id] += 1
				break


		if selected == False: continue

		logger.info("Selected substructure: \n{}".format(s.pretty_print()))

		available_substitutions = sim_available_substitutions
		logger.info("Available substitutions: {}".format(len(available_substitutions)))
		logger.info("Substitutions applied so far: {}".format(count_substitutions))
		logger.info("\n{}".format(generated_structure.pretty_print()))

		count_substitutions += 1

		if count_substitutions >= minimum_count:
			logger.info("Over minimum structure limit. Trying to combine g_f...")
			for connecting in sorted(generated_structure.connecting, key=lambda x: x.c, reverse=True):
				if connecting.edges[0].properties["combined"] == None:
					for s_id, n2 in connecting.edges[0].properties["combinable"]:
						if s_id == g_f.id:
							generated_structure.expand(g_f, connecting, n2)
							return generated_structure, substructures_used, count_substitutions

	return generated_structure, substructures_used, count_substitutions

def instantiate_base_level(id_substructures):
	g_s = Substructure(id_substructures)

	for c in range(3):
		platform = Node(15, c, "X")
		platform.type = "Solid"
		platform.cluster_id = g_s.id
		g_s.insert_node(platform)

	mario = Node(14, 1, "M")
	mario.cluster_id = g_s.id
	g_s.insert_node(mario)

	connecting = Node(15, 3, "*", g_s.id, 0, 0, "Connecting")
	connecting.add_edge(connecting, {"direction":"r", "combined":None, "combinable":[]})
	g_s.insert_node(connecting)

	id_substructures += 1

	g_f = Substructure(id_substructures)

	for c in range(1, 3):
		platform = Node(15, c, "X")
		platform.type = "Solid"
		platform.cluster_id = g_f.id
		g_f.insert_node(platform)

	finish = Node(14, 2, "F")
	finish.cluster_id = g_f.id
	g_f.insert_node(finish)

	connecting = Node(15, 0, "*", g_f.id, 0, 0, "Connecting")
	connecting.id =  g_f.id
	connecting.add_edge(connecting, {"direction":"l", "combined":None, "combinable":[]})
	g_f.insert_node(connecting)

	return g_s, g_f
