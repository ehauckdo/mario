#import substructure_manipulation
import logging
import copy
from .level import Level
logger = logging.getLogger(__name__)

# class Node:
#
# 	def __init__(self):
# 		pass
#
# 	def __init__(self, r, c, tile=None, c_id=0, d=0, s=0, t="P"):
# 		self.r = r
# 		self.c = c
# 		self.tile = tile
# 		self.type = t
# 		self.edges = []
# 		self.substructure_id = c_id
# 		self.d = d # distance from core node
# 		self.s = s # similarity measure
#
# 	def __repr__(self):
# 		return "({},{})".format(self.r, self.c)
#
# 	def add_edge(self, n2, properties):
# 		edge = Edge(self, n2, properties)
# 		self.edges.append(edge)

class Edge:
	def __init__(self):
		pass

	def __init__(self, n1, n2, properties={}):
		self.n1 = n1
		self.n2 = n2
		self.properties = properties

	def __repr__(self):
		return "{} :{}".format(self.n2,self.properties)

class Connector:
	def __init__(self, r, c, direction, substruture_id=0):
		self.r = r
		self.c = c
		self.direction = direction
		self.combined = None
		self.combinable = []
		self.substructure_id = substructure_id

class Node:
	def __init__(self, r, c, tile="-", type="Non-Solid", substructure_id=0):
		self.r = r
		self.c = c
		self.tile = tile
		self.type = type
		self.substructure_id = substructure_id
		self.edges = []

	def __repr__(self):
		return "({},{})".format(self.r, self.c)

	def add_edge(self, n2, properties):
		edge = Edge(self, n2, properties)
		self.edges.append(edge)

class Substructure:

	def __init__(self, substructure_id):
		self.id = substructure_id
		self.nodes = []
		self.connecting = []

	def insert_node(self, n):
		if n.type != "Connecting":
			self.nodes.append(n)
		else:
			self.connecting.append(n)

	def relativize_coordinates(self):
		"""Shift all nodes so the left-most node has column==0"""
		if len(self.nodes) + len(self.connecting) < 1:
			return
		smallest_c = (self.nodes+self.connecting)[0].c
		for node in self.nodes+self.connecting:
			if node.c < smallest_c:
				smallest_c = node.c
		for node in self.nodes+self.connecting:
			node.c = node.c - smallest_c

	def adjust(self, s2, c1, c2):
		horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
		vertical = {"r": 0, "l": 0, "u": -1, "d": 1}
		s1 = self

		n1_direction = c1.edges[0].properties["direction"]
		n2_direction = c2.edges[0].properties["direction"]

		adjust_column = (c1.c + (horizontal[n1_direction])) - c2.c
		adjust_row = (c1.r + (vertical[n2_direction])) - c2.r

		s2_adjusted = copy.deepcopy(s2)

		# c1.edges[0].properties["combinable"].remove((s2.id, c2))

		for c in s2_adjusted.connecting:
			if c.r == c2.r and c.c == c2.c:
			#if c == c2:
				logger.info("S1: {}, c1: {}".format(c1.substructure_id, c1))
				logger.info("S2: {}, c2: {}".format(c2.substructure_id, c2))

				logger.info("S1 combinables BEFORE: ")
				logger.info(c1.edges[0].properties["combinable"])
				c1.edges[0].properties["combined"] = [s2_adjusted, c]
				c1.edges[0].properties["combinable"].remove((s2.id, c2))
				logger.info("S1 combinables AFTER: ")
				logger.info(c1.edges[0].properties["combinable"])

				logger.info("S2 combinables BEFORE: ")
				logger.info(c.edges[0].properties["combinable"])
				c.edges[0].properties["combined"] = [s1, c1]
				for c_id, connecting in c.edges[0].properties["combinable"]:
					if c_id == c1.substructure_id and connecting.r == c1.r and connecting.c == c1.c:
						c.edges[0].properties["combinable"].remove((c_id, connecting))

				#c.edges[0].properties["combinable"].remove((c1.substructure_id, c1))
				logger.info("S2 combinables AFTER: ")
				logger.info(c.edges[0].properties["combinable"])

				logger.info("Removing c1 from s1 ({}, {}) from s2".format(s1.id,c1))
				logger.info("Removing c2 from s2 ({}, {}) from s1".format(s2.id,c))

				# for combinable in c.edges[0].properties["combinable"]:
				# 	logger.info("Comparing ({}, {}) against {}:".format(s1.id,c1, combinable))
				#
				# 	if s1.id == combinable[0]:
				# 		logger.info("Id Equal")
				# 	else:
				# 		logger.info("Id Not Equal")
				# 	if c1 == combinable[1]:
				# 		logger.info("C Equal")
				# 	else:
				# 		logger.info("C Not Equal")
				# 		logger.info("Edges c1:")
				# 		for key in c1.edges[0].properties.keys():
				# 			logger.info("Key: {}, Value: {}".format(key, c1.edges[0].properties[key]))
				# 		logger.info("Edges combinable[1]:{}")
				# 		for key in combinable[1].edges[0].properties.keys():
				# 			logger.info("Key: {}, Value: {}".format(key, combinable[1].edges[0].properties[key]))
				#
				# c.edges[0].properties["combinable"].remove((s1.id,c1))
				# c1.edges[0].properties["combinable"].remove((s2.id,c))
				break

		s2_adjusted.adjust_columns(adjust_column)
		s2_adjusted.adjust_rows(adjust_row)

		for i in range(len(s2_adjusted.nodes)-1, -1, -1):
			n = s2_adjusted.nodes[i]
			if n.r < 0 or n.r > 15 or n.c < 0:
				s2_adjusted.nodes.remove(n)

		for i in range(len(s2_adjusted.connecting)-1, -1, -1):
			n = s2_adjusted.connecting[i]
			if n.r < 0 or n.r > 15 or n.c < 0:
				s2_adjusted.connecting.remove(n)



		return s2_adjusted#, collides

	def expand(self, s2, c1, c2):
		#logger.info("Connecting structure {} with {} by using connecting nodes {} and {}".format(self.id, s2.id, c1, c2))

		s2_adjusted = self.adjust(s2, c1, c2)

		self.nodes.extend(s2_adjusted.nodes)
		self.connecting.extend(s2_adjusted.connecting)

		collides = False
		level_matrix = {}
		for n in self.nodes:
			if (n.r, n.c) not in level_matrix.keys():
				level_matrix[(n.r,n.c)] = n.tile
			else:
				collides = True

		sim_available_substitutions = self.get_available_substitutions()

		return s2_adjusted, collides, sim_available_substitutions

	def get_available_substitutions(self):
		substituions = []
		for n in self.connecting:
			if n.edges[0].properties["combined"] == None:
				for s_id, n2 in n.edges[0].properties["combinable"]:
					substituions.append((n, s_id, n2))
		return substituions

	def adjust_columns(self, adjust):
		for n in self.nodes+self.connecting:
			n.c += adjust

	def adjust_rows(self, adjust):
		for n in self.nodes+self.connecting:
			n.r += adjust

	def __repr__(self):
		return "ID: {}\n Nodes: {}\n Connecting Nodes: {}".format(self.id,self.nodes, self.connecting)

	def matrix_representation(self):
		generated = Level(" ")

		for n in self.nodes:
			generated.set(n.r, n.c, n.tile)
		directions = {"r":">", "l":"<", "u":"^", "d":"v"}
		for n in self.connecting:
			generated.set(n.r, n.c, directions[n.edges[0].properties["direction"]])

		return generated.matrix_representation()

	def level_representation(self, filler=True):
		# 1: find the highest column values
		highest_column = 0
		for n in self.nodes + self.connecting:
			if n.c > highest_column:
				highest_column = n.c

		# 2: create a matrix with [16][n_columns]
		base_tile = "-" if filler else " "
		level = [[" " for i in range(highest_column+1)] for j in range(16)]

		# 3: fill the matrix with * where * is a
		# placeholder image (maybe an empty 17x16 png)

		# 4: iterate over all nodes and place tiles in
		# the appropriate locations in the matrix
		directions = {"r":">", "l":"<", "u":"^", "d":"v"}
		for n in self.nodes:
			level[n.r][n.c] = n.tile
		for n in self.connecting:
			level[n.r][n.c] = directions[n.edges[0].properties["direction"]]

		# 5: return the matrix, to be used in render_level
		return level

	def pretty_print(self, filler=True):

		level = self.level_representation(filler)
		full_string = ""

		for row in level:
			row_str = ""
			for tile in row:
				row_str += tile
			full_string += row_str + "\n"

		return full_string

		# generated = Level()
		#
		# for n in self.nodes:
		# 	# print("Inserting node: {},{}".format(n.r, n.c))
		#
		# 	generated.set(n.r, n.c, n.tile if symbols==True else (self.id if n.d != 0 else "#"))
		# directions = {"r":">", "l":"<", "u":"^", "d":"v"}
		# for n in self.connecting:
		# 	generated.set(n.r, n.c, directions[n.edges[0].properties["direction"]])
		#
		# return generated.pretty_print()

	def pretty_print_nodes(self, symbols=True):
		generated = Level()
		directions = {"r":">", "l":"<", "u":"^", "d":"v"}

		for n in self.nodes:
			# print("Inserting node: {},{}".format(n.r, n.c))
			generated.set(n.r, n.c, n.tile if symbols==True else (self.id if n.d != 0 else "#"))
		for n in self.connecting:
			generated.set(n.r, n.c, directions[n.edges[0].properties["direction"]])

		# horrible, horrible hack
		for i in range(len(generated.map_data)):
				generated.map_data[i] = " "
		for n in self.nodes:
			generated.set(n.r, n.c, n.tile if symbols==True else (self.id if n.d != 0 else "#"))
		for n in self.connecting:
			generated.set(n.r, n.c, directions[n.edges[0].properties["direction"]])

		return generated.pretty_print()

	def save_as_level(self, level_filename="output.txt"):
		generated = Level()

		for n in self.nodes:
			# print("Inserting node: {},{}".format(n.r, n.c))
			generated.set(n.r, n.c, n.tile)

		generated.save_level(level_filename)
