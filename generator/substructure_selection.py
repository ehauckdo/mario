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

def pretty_print_graph_map_rect(graph_map, tiles=False):

	import string
	symbols = {0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"f", 6:"g", 7:"h"}
	size = len(string.ascii_lowercase)

	if tiles:
		row = "\n"
		for g in graph_map:
			for v in g:
				if v == None: row += " "
				else: row += "{}".format(v)
			row += "\n"
		logger.info(row)

	else:
		row = "\n"
		for g in graph_map:
			for v in g:
				if v == None: row += " "
				else: row += "{}".format(string.ascii_lowercase[v%size])
			row += "\n"
		logger.info(row)

def update_graph_map(graph_map, id, x_min, x_max, y_min, y_max):
	collisions = []
	if x_min < 0 or y_min < 0:
		raise IndexError
	for x in range(x_min, x_max+1):
		for y in range(y_min, y_max+1):
			if graph_map[x][y] != None and graph_map[x][y] != id:
				logger.info("Collision at x {}, y {}: {}".format(x,y, graph_map[x][y]))
				collisions.append([graph_map[x][y],x, y])

	if len(collisions) == 0:
		for x in range(x_min, x_max+1):
			for y in range(y_min, y_max+1):
				graph_map[x][y] = id

	# remove duplicates from list
	if len(collisions) > 0:
		collisions = dict((x[0], x) for x in collisions).values()

	pretty_print_graph_map_rect(graph_map)
	return collisions

def get_substructures_rect(map_data, points, D=5, S=2):

	graph_map = [[None for i in range(map_data.n_cols)] for i in range(map_data.n_rows)]

	cluster_collisions = {}
	cluster_id = 1

	clusters = []
	finished_clusters = []
	#moves = {"LEFT":"DOWN", "DOWN":"RIGHT", "RIGHT":"UP", "UP":"LEFT"}
	effects = {"LEFT":(0,-1), "DOWN":(1,0), "RIGHT":(0,1), "UP":(-1,0)}

	for p in points:
		# set id of cluster in graph map
		graph_map[p[0]][p[1]] = cluster_id

		# initialize an empty list to save collisions of this cluster
		cluster_collisions[cluster_id] = {}
		logger.debug(" Setting core point (id {}) x: {}, y: {}".format(cluster_id, p[0],p[1]))
		# fields: id, x_min, x_max, y_min, y_max
		clusters.append([cluster_id, p[0], p[0], p[1], p[1], {"LEFT":"DOWN", "DOWN":"RIGHT", "RIGHT":"UP", "UP":"LEFT"}, "UP"])

		cluster_id += 1

	pretty_print_graph_map_rect(graph_map)

	while len(clusters) > 0:
	#for i in range(500):
		# get the first cluster reference from the list
		id, r_min, r_max, c_min, c_max, moves, prev_move = clusters.pop(0)
		move = moves[prev_move]
		logger.info("id: {}, r_min: {}, r_max:{}, c_min:{}, c_max:{}, move: {}".format(id, r_min, r_max, c_min, c_max, move))
		logger.info("Move list: {}".format(moves))
		# obtain the delta values for x and y
		delta_r, delta_c = effects[move]

		r_min_new = r_min + delta_r if delta_r < 0 else r_min
		r_max_new = r_max + delta_r if delta_r > 0 else r_max
		c_min_new = c_min + delta_c if delta_c < 0 else c_min
		c_max_new = c_max + delta_c if delta_c > 0 else c_max

		#logger.info("r_min_new: {}, r_max_new:{}, c_min_new:{}, c_max_new:{}".format(r_min_new, r_max_new, c_min_new, c_max_new))

		# change is on the y coordinate
		#if delta_c == 0:
			#logger.info("Y is the same")
			#for y in range(c_min_new, c_max_new+1):
			#	logger.info("New node: x:{}, y:{}".format(r_min_new, y))
		#	clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves[move]])

		#if delta_r == 0:
			#logger.info("X is the same")
			#for x in range(r_min_new, r_max_new+1):
			#	logger.info("New node: x:{}, y:{}".format(x, c_max_new))
		#	clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves[move]])

		logger.info("Tentative: r_min: {}, r_max:{}, c_min:{}, c_max:{}".format(r_min_new, r_max_new, c_min_new, c_max_new))
		try:
			collisions = update_graph_map(graph_map, id, r_min_new, r_max_new, c_min_new, c_max_new)
			if len(collisions) > 0:
				logger.info("Found collisions between when expanding structure {}".format(id))
				for other_id, r, c in collisions:
					if other_id not in cluster_collisions[id].keys():
						cluster_collisions[id][other_id] = (r, c)
						other_r = r + 1 if move == "UP" else r - 1 if move == "DOWN" else r
						other_c = c + 1 if move == "RIGHT" else c - 1 if move == "LEFT" else c
						cluster_collisions[other_id][id] = (other_r, other_c)
						# create connecting nodes here in the appropriate locations
						logger.info("Expanding Structure structure {}, r {}, c {}".format(id, other_r, other_c))
						logger.info("Collided structure {}, r {}, c {}".format(other_id, r, c))
				next_move = moves[move]
				if move == next_move:
					logger.info("Cluster has finished expansion.")
					finished_clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new])
				else:
					moves[prev_move] = next_move
					move = prev_move
					r_min_new = r_min
					r_max_new = r_max
					c_min_new = c_min
					c_max_new = c_max
					clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves, move])

			else:
				logger.info("No collisions found. Proceeding regular expansion...")
				clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves, move])

		except IndexError:
			logger.info("Accessing invalid index. Reverting expansion")
			next_move = moves[move]
			if move == next_move:
				logger.info("Cluster has finished expansion.")
				finished_clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new])
			else:
				moves[prev_move] = next_move
				move = prev_move
				r_min_new = r_min
				r_max_new = r_max
				c_min_new = c_min
				c_max_new = c_max
				clusters.append([id, r_min_new, r_max_new, c_min_new, c_max_new, moves, move])

	logger.info("Clusters at the end of expansions: ")
	for id, r_min, x_max, c_min, c_max in finished_clusters:
		logger.info("id: {}, r_min: {}, r_max:{}, c_min:{}, c_max:{}, move: {}".format(id, r_min, x_max, c_min, c_max, move))

	logger.info("All connecting nodes to-be created:")
	for id in cluster_collisions.keys():
		logger.info("Structure {}:".format(id))
		for other_id in cluster_collisions[id].keys():
			r, c = cluster_collisions[id][other_id]
			logger.info("- Connecting node with {} at r: {}, c: {}".format(other_id, r, c))

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
		#directions = [("d",r+1,c), ("r",r, c+1), ("u",r-1, c), ("l",r, c-1), ("r",r+1,c+1), ("r",r-1, c+1), ("l",r-1, c-1), ("l",r+1, c-1)]
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

						node_1.add_edge(node_2, {"direction":direc, "combined":None, "combinable":[]})
						oppos_direc = switcher[direc]
						node_2.add_edge(node_1, {"direction":oppos_direc, "combined":None, "combinable":[]})

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
