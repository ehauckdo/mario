#import substructure_manipulation

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

		import copy
		s2_adjusted = copy.deepcopy(s2)

		for c in self.connecting:
			if c.r == c1.r and c.c == c1.c:
				# print("Deleting connecting node from s1")
				self.connecting.remove(c)
				break
		for c in s2_adjusted.connecting:
			if c.r == c2.r and c.c == c2.c:
				# print("Deleting connecting node from s2")
				s2_adjusted.connecting.remove(c)
				break
				

		#s2_adjusted = substructure_manipulation.adjust_substructure_columns(s2_adjusted, adjust_column)

		#s2_adjusted = substructure_manipulation.adjust_substructure_rows(s2_adjusted, adjust_row)

		s2_adjusted.adjust_columns(adjust_column)
		s2_adjusted.adjust_rows(adjust_row)

		return s2_adjusted

	def collides(self, s2, c1, c2):

		map_matrix = [{} for i in range(16)]
		s2_adjusted = self.adjust(s2, c1, c2)

		for n in s2.nodes:
			map_matrix[n.r][n.c] = n.tile

		for n in self.nodes:
			try:
				if map_matrix[n.r][n.c] != None:
					return True
			except:
				pass
		return False

	def get_available_substitutions(self):
		substituions = []
		for n in self.connecting:
			for s_id, n2 in n.edges[0].properties["combinable"]:
				substituions.append((n, s_id, n2))
		return substituions

	def adjust_columns(self, adjust):
		for n in self.nodes+self.connecting:
			n.c += adjust

	def adjust_rows(self, adjust):
		for n in self.nodes+self.connecting:
			n.r += adjust

	def expand(self, s2, c1, c2):
		print("Connecting")
		print(self)
		print("With")
		print(s2)
		print("By using connecting nodes {}  and  {}".format(c1, c2))

		s2_adjusted = self.adjust(s2, c1, c2)

		# horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
		# vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

		# n1_direction = c1.edges[0].properties["direction"]
		# n2_direction = c2.edges[0].properties["direction"]

		# adjust_column = (c1.c + (horizontal[n1_direction])) - c2.c
		# adjust_row = (c1.r + (vertical[n2_direction])) - c2.r

		# import copy
		# s2_adjusted = copy.deepcopy(s2)

		# for c in self.connecting:
		# 	if c.r == c1.r and c.c == c1.c:
		# 		# print("Deleting connecting node from s1")
		# 		self.connecting.remove(c)
		# 		break
		# for c in s2_adjusted.connecting:
		# 	if c.r == c2.r and c.c == c2.c:
		# 		# print("Deleting connecting node from s2")
		# 		s2_adjusted.connecting.remove(c)
		# 		break
				

		# s2_adjusted = substructure_manipulation.adjust_substructure_columns(s2_adjusted, adjust_column)

		# s2_adjusted = substructure_manipulation.adjust_substructure_rows(s2_adjusted, adjust_row)

		print("Adjusted s2: ")
		print(s2_adjusted)

		self.nodes.extend(s2_adjusted.nodes)
		self.connecting.extend(s2_adjusted.connecting)
		
		print("Updated Structure:")
		print(self)

		return

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

	def pretty_print(self, symbols=True):
		full_string = "#"
		from map import Generated_Map
		generated = Generated_Map()

		for n in self.nodes:
			# print("Inserting node: {},{}".format(n.r, n.c))
			
			generated.set(n.r, n.c, n.tile if symbols==True else (self.id if n.d != 0 else "#"))

		return generated.pretty_print()

	def save_as_map(self, map_filename="output.txt"):
		from map import Generated_Map
		generated = Generated_Map()

		for n in self.nodes:
			# print("Inserting node: {},{}".format(n.r, n.c))
			generated.set(n.r, n.c, n.tile)

		generated.save_map(map_filename)