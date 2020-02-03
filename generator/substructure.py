#import substructure_manipulation
import logging
import copy
from .level import Level
logger = logging.getLogger(__name__)

class Node:

	def __init__(self):
		pass

	def __init__(self, r, c, tile=None, c_id=0, d=0, s=0, t="P"):
		self.r = r
		self.c = c
		self.tile = tile
		self.type = t
		self.edges = []
		self.cluster_id = c_id
		self.d = d # distance from core node
		self.s = s # similarity measure

	def __repr__(self):
		return "({},{})".format(self.r, self.c)

	def add_edge(self, n2, properties):
		edge = Edge(self, n2, properties)
		self.edges.append(edge)

class Edge:
	def __init__(self):
		pass

	def __init__(self, n1, n2, properties={}):
		self.n1 = n1
		self.n2 = n2
		self.properties = properties

	def __repr__(self):
		return "{} :{}".format(self.n2,self.properties)


class Substructure:

	def __init__(self, substructure_id):
		self.id = substructure_id
		self.nodes = []
		self.connecting = []
		self.combinable = []

	def insert_node(self, n):
		if n.type != "Connecting":
			self.nodes.append(n)
		else:
			self.connecting.append(n)

	def adjust(self, s2, c1, c2):
		horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
		vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

		n1_direction = c1.edges[0].properties["direction"]
		n2_direction = c2.edges[0].properties["direction"]

		adjust_column = (c1.c + (horizontal[n1_direction])) - c2.c
		adjust_row = (c1.r + (vertical[n2_direction])) - c2.r

		s2_adjusted = copy.deepcopy(s2)

		for c in s2_adjusted.connecting:
			if c.r == c2.r and c.c == c2.c:
				c1.edges[0].properties["combined"] = [s2_adjusted, c]
				c.edges[0].properties["combined"] = [self, c1]
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

		return s2_adjusted

	def collides(self, s2, c1, c2):
		# logger.debug("Checking collision between structures: ")
		map_matrix = [{} for i in range(16)]

		s2_adjusted = copy.deepcopy(s2)

		horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
		vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

		n1_direction = c1.edges[0].properties["direction"]
		n2_direction = c2.edges[0].properties["direction"]

		# logger.debug("Connecting (s1) n1: {}, direction: {}".format(c1, n1_direction))
		# logger.debug("Connecting (s2) n2: {}, direction: {}".format(c2, n2_direction))

		adjust_column = (c1.c + (horizontal[n1_direction])) - c2.c
		adjust_row = (c1.r + (vertical[n2_direction])) - c2.r

		s2_adjusted.adjust_columns(adjust_column)
		s2_adjusted.adjust_rows(adjust_row)

		for n in s2_adjusted.nodes:
			#logger.debug(n)
			try:
				map_matrix[n.r][n.c] = n.tile
			except:
				# out of bounds, we can ignore
				pass

		for n in self.nodes:
			try:
				if map_matrix[n.r][n.c] != None:
					return True
			except:
				pass

		return False

	def expand(self, s2, c1, c2):
		#logger.info("Connecting structure {} with {} by using connecting nodes {} and {}".format(self.id, s2.id, c1, c2))

		s2_adjusted = self.adjust(s2, c1, c2)

		self.nodes.extend(s2_adjusted.nodes)
		self.connecting.extend(s2_adjusted.connecting)

		return s2_adjusted

	def simulate_adjust_columns(self, adjust):
		for index in range(len(self.nodes)-1, -1, -1):
			n = self.nodes[index]
			n.c += adjust
			if n.c < 0:
				self.nodes.remove(n)

		for index in range(len(self.connecting)-1, -1, -1):
			n = self.connecting[index]
			n.c += adjust
			if n.c < 0:
				self.connecting.remove(n)

	def simulate_adjust_rows(self, adjust):
		for index in range(len(self.nodes)-1, -1, -1):
			n = self.nodes[index]
			n.r += adjust
			if n.r < 0 or n.r > 15:
				self.nodes.remove(n)

		for index in range(len(self.connecting)-1, -1, -1):
			n = self.connecting[index]
			n.r += adjust
			if n.r < 0 or n.r > 15:
				self.connecting.remove(n)

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

	def relativize_coordinates(self):

		if len(self.nodes) + len(self.connecting) < 1:
			return

		smallest_c = (self.nodes+self.connecting)[0].c

		for node in self.nodes+self.connecting:
			if node.c < smallest_c:
				smallest_c = node.c

		for node in self.nodes+self.connecting:
			node.c = node.c - smallest_c

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
