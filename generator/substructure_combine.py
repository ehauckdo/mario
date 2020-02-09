import logging
import copy
from .reachability import is_reachable
logger = logging.getLogger(__name__)

def group_by_direction(connecting_nodes_list):
	directions = {"r":[], "l":[], "u":[], "d":[]}
	for c_id in connecting_nodes_list.keys():
		print("Cluster {}".format(c_id))
		connecting_nodes = connecting_nodes_list[c_id]
		for n in connecting_nodes:
			edge = n.edges[0]
			d = edge.properties["direction"]
			directions[d].append((c_id, n))

	return directions

def do_overlap(s1, s2):
	# TODO: improve performance by building a matrix
	for n1 in s1.nodes:
		for n2 in s2.nodes:
			if n1.c == n2.c and n1.r == n2.r:
				#return False
				logger.debug(">>> Overlap Ocurred between structures {} and {}".format(s1.id, s2.id))
				return True
	return False

def are_combinable(s1, s2, n1, n2, d1, d2):
	logger.debug("Checking combinability of {} (id{}) and {} (id{})".format(n1, s1.id, n2, s2.id))

	logger.debug("Before adjustment: ")
	logger.debug(s2.nodes+s2.connecting)

	horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
	vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

	adjust_col = (n1.c + (horizontal[d1])) - n2.c
	adjust_row = (n1.r + (vertical[d1])) - n2.r

	s2_adjusted = copy.deepcopy(s2)

	#s2_adjusted.adjust(s2, n1, n2)

	s2_adjusted.adjust_columns(adjust_col)
	s2_adjusted.adjust_rows(adjust_row)

	for i in range(len(s2_adjusted.nodes)-1, -1, -1):
		n = s2_adjusted.nodes[i]
		if n.r < 0 or n.r > 15 or n.c < 0:
			s2_adjusted.nodes.remove(n)

	for i in range(len(s2_adjusted.connecting)-1, -1, -1):
		n = s2_adjusted.connecting[i]
		if n.r < 0 or n.r > 15 or n.c < 0:
			s2_adjusted.connecting.remove(n)

	logger.debug("After adjustment: ")
	logger.debug(s2_adjusted.nodes+s2_adjusted.connecting)

	# Check collisions and reachability between s1 and s2
	if not do_overlap(s1, s2_adjusted) and is_reachable(s1, s2_adjusted):
		return True
	else:
		return False

def find_substructures_combinations(substructures):

	main_directions = {"r", "u"}
	opposite_directions = {"r":"l", "l":"r", "u":"d", "d":"u"}

	connecting_nodes = []
	for s in substructures:
		connecting_nodes.extend(s.connecting)

	# go through all substructures checking connecting nodes
	for s1 in substructures:
	#for index1 in range(len(substructures)-1):
		#s1 = substructures[index1]
		logger.debug("-Start: connecting substructures in {}".format(s1.id))

		for n1 in s1.connecting:
			direction = n1.edges[0].properties["direction"]
			logger.debug("--Start: Processing connecting node {}, direction: {}".format(n1, direction))

			if direction not in main_directions:
				logger.debug("--Finish: Processing connecting node {}".format(n1))
				continue
			opposite = opposite_directions[direction]

			# for a certain connecting node n1, go through all substructures
			# again and search for a connecting node n2 that has opposite
			# direction
			for s2 in substructures:
				if s1.id == s2.id: continue

				for n2 in s2.connecting:
					n2_direction = n2.edges[0].properties["direction"]

					# second condition ensures that both substructures
					# are connecting at the same height/
					if n2_direction == opposite:
						if n2_direction == "d" or n1.r == n2.r:
							logger.debug("---Opposing Node: {}, Direction: {}".format(n2, n2_direction))

							combinable = are_combinable(s1, s2, n1, n2, direction, opposite)

							if combinable:
								logger.info("--- Combinable ({}): n1 {}, ({}): n2 {}".format(s1.id, n1, s2.id, n2))
								n1.edges[0].properties["combinable"].append((s2.id, n2))
								n2.edges[0].properties["combinable"].append((s1.id, n1))
							else:
								logger.debug("--- Not combinable")

			logger.debug("--Finish: Processing connecting node {}".format(n1))
		logger.debug("-Finish: connecting substructures in {}".format(s1.id))
