import logging
from .substructure import Substructure, Node
logger = logging.getLogger(__name__)

def pretty_print_graph_map(graph_map, tiles=False):

	import string
	symbols = {0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"f", 6:"g", 7:"h"}
	size = len(string.ascii_lowercase)

	if tiles:
		row = ""
		for g in graph_map:
			for v in g:
				if v == None: row += " "
				else: row += "{}".format(v.tile)
			row += "\n"
		logger.info(row)

	else:
		row = ""
		for g in graph_map:
			for v in g:
				if v == None: row += " "
				else: row += "{}".format(string.ascii_lowercase[v.cluster_id%size])
			row += "\n"
		logger.info(row)

def append_adjacent_edges(graph_map):

	for r in range(len(graph_map)):
		for c in range(len(graph_map[r])):
			n = graph_map[r][c]

			directions = [("r",r,c+1),("d",r+1, c),("l",r, c-1),("u",r-1, c)]

			for direction, neigh_r, neigh_c in directions:
				try:
					if graph_map[neigh_r][neigh_c] != None:
						neighbour = graph_map[neigh_r][neigh_c]
						n.add_edge(neighbour, {"direction":direction})
				except:
					pass

def generate_substructures(graph_map, connecting_nodes):
	substructures = {}

	for r in range(len(graph_map)):
		for c in range(len(graph_map[r])):
			n = graph_map[r][c]

			if n != None:
				if n.cluster_id not in substructures.keys():
					substructures[n.cluster_id] = Substructure(n.cluster_id)

				substructures[n.cluster_id].insert_node(n)

	for connecting in connecting_nodes:
		substructures[connecting.cluster_id].insert_node(connecting)

	return list(substructures.values())


def get_substructures(map_data, points, D=5, S=2):

	platform_blocks = ["X", '#', 't', "Q", "S", "?", "U"]

	nodes = []
	all_expanded_nodes = []
	cluster_collisions = {}
	connecting_nodes = []

	cluster_id = 1
	graph_map = [[None for i in range(map_data.n_cols)] for i in range(map_data.n_rows)]

	#pretty_print_graph_map(graph_map)

	def get_substructures_by_cluster_id(node_list):
		clusters = {}

		for n in node_list:
			if n.cluster_id not in clusters.keys():
				clusters[n.cluster_id] = []

			clusters[n.cluster_id].append(n)

		return clusters

	def expand(node):

		r, c = node.r, node.c
		directions = [("d",r+1,c), ("r",r, c+1), ("u",r-1, c), ("l",r, c-1)]
		switcher = {"r":"l", "l":"r", "u":"d", "d":"u"}
		n_rows, n_cols = map_data.n_rows, map_data.n_cols

		for direc, row, col in directions:
			if row > 0 and row < n_rows and col > 0 and col < n_cols:

				s = node.s
				d = node.d
				if node.d <= D:
					d += 1
				else:
					if node.d+node.s >= D+S: continue
					elif node.tile == map_data.get(row, col) and node.tile != "-":
							s += 1
					else: continue

				if graph_map[row][col] == None:
					tile = map_data.get(row, col)
					child = Node(row, col, tile, node.cluster_id, d, s, "Solid" if tile in platform_blocks else "Non-Solid")
					graph_map[row][col] = child

					nodes.append(child)

				else:

					collided_id = graph_map[row][col].cluster_id
					current_id = node.cluster_id

					if collided_id != current_id and collided_id not in cluster_collisions[current_id]:

						# Create a connecting node for the current cluster
						# in the pos where the other cluster's node exists
						node_1 = Node(row, col, "*", node.cluster_id, d, s, "Connecting")
						#node_1.cluster_id = current_id
						#node_1.d = d
						node_1.connectors = []
						connecting_nodes.append(node_1)

						# Create anoter connecting node for the other cluster
						# in the pos of the current cluster's node
						node_2 = Node(r, c, "*", collided_id, d, s, "Connecting")
						#node_2.cluster_id = collided_id
						#node_2.d = d
						node_2.connectors = []
						connecting_nodes.append(node_2)

						node_1.add_edge(node_2, {"direction":direc, "combinable":[]})
						oppos_direc = switcher[direc]
						node_2.add_edge(node_1, {"direction":oppos_direc, "combinable":[]})

						cluster_collisions[current_id].append(collided_id)
						cluster_collisions[collided_id].append(current_id)

	logger.debug("Points to be expanded into substructures: ")
	for p in points:
		# create a core node for each of the points passed
		node = Node(p[0], p[1], map_data.get(p[0], p[1]), cluster_id, 0, 0)
		#node.cluster_id = cluster_id
		cluster_collisions[cluster_id] = []
		cluster_id += 1
		graph_map[p[0]][p[1]] = node

		nodes.append(node)
		logger.debug(" id: {}, x: {}, y: {}, tile: {}".format(node.cluster_id, p[0],p[1], node.tile))

	while len(nodes) > 0:

		current = nodes.pop(0)
		expand(current)

	pretty_print_graph_map(graph_map)

	logger.debug("Collisions during 1st expansion step:")
	for c_id in cluster_collisions.keys():
		collisions = cluster_collisions[c_id]
		logger.debug("Substructure {}: {}".format(c_id, collisions))


	append_adjacent_edges(graph_map)

	substructures = generate_substructures(graph_map, connecting_nodes)

	# logger.info("Generated Substructures: ")
	# for s in substructures:
	# 	logger.info(s)

	#substructures = get_substructures_by_cluster_id(all_expanded_nodes)

	return substructures
