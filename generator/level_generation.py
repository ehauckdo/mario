import logging
import random
from .substructure import Substructure, Node

logger = logging.getLogger(__name__)

def generate_levels(substructures, g_s, g_f, n_maps):

	for i in range(n_maps):

		output_file = open("output/output_{}_stats.txt".format(i), "w")
		substructures_used = {}
		for s in substructures:
			substructures_used[s.id] = 0
		substructures_used[g_s.id] = 0
		substructures_used[g_f.id] = 0

		logger.info("Generating map {}".format(i))

		import copy
		generated_structure = copy.deepcopy(g_s)
		logger.info("Initial structure generated! \n{}". format(generated_structure.pretty_print()))

		available_substitutions = generated_structure.get_available_substitutions()
		count_substitutions = 0
		logger.info("Starting substitution process...")

		while len(available_substitutions) > 0:

			# TODO find a better way of selecting structures with
			# more than 1 connecting node
			selected = False
			while len(available_substitutions) > 0:
				c1, s_id, c2 = random.choice(available_substitutions)
				available_substitutions.remove((c1,s_id, c2))
				for s in substructures:
					if s.id == s_id:
						break

				sim_structure, collides = generated_structure.simulate_expansion(s, c1, c2)
				sim_available_substitutions = sim_structure.get_available_substitutions()
				if collides: #or len(sim_available_substitutions) <= 0:
					# logger.info("Simulated structure has connecting <= 0 or collides, trying next...")
					logger.info("Simulated structure collides, trying next...")
					continue
				else:

					generated_structure = sim_structure
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

			if count_substitutions >= 30:
				for connecting in generated_structure.connecting:
					for s_id, n2 in connecting.edges[0].properties["combinable"]:
						if s_id == g_f.id:
							generated_structure.expand(g_f, connecting, n2)
							available_substitutions = []
							break


		for s_id, value in sorted(substructures_used.items()):
			print("{}: {}".format(s_id, value), file=output_file)

		output_file.close()

		generated_structure.save_as_level("output/output_{}.txt".format(i))

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
	connecting.add_edge(connecting, {"direction":"r", "combinable":[]})
	g_s.insert_node(connecting)

	id_substructures += 1

	g_f = Substructure(id_substructures)

	for c  in range(2,4):
		platform = Node(11, c, "X")
		platform.type = "Solid"
		platform.cluster_id = g_f.id
		g_f.insert_node(platform)

	finish = Node(10, 2, "F")
	finish.cluster_id = g_f.id
	g_f.insert_node(finish)

	connecting = Node(15, 0, "*", g_f.id, 0, 0, "Connecting")
	connecting.id =  g_f.id
	connecting.add_edge(connecting, {"direction":"l", "combinable":[]})
	g_f.insert_node(connecting)

	return g_s, g_f
