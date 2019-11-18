#import map_matrix, grammar
import os
import sys
import optparse
import math
import logging, inspect
import random

from point_selection import get_points
from substructure_selection import get_substructures, pretty_print_graph_map
from substructure_combine import find_substructures_combinations

# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Map:

	def __init__(self):
		self.map_data = []
		self.n_rows = 16
		self.n_cols = 1

	def append(self, value):
		self.map_data.append(value)
		self.n_cols = math.ceil(len(self.map_data) / self.n_rows)

	def get(self, x, y):
		if x > self.n_rows or y > self.n_cols:
			raise "Accessing invalid index"
		index = self.n_rows * y + x
		return self.map_data[index]

	def pretty_print(self):
		for i in range(self.n_rows):
			row = ""
			for j in range(self.n_cols):
				tile = self.get(i, j)
				row += tile
			print(row)

def parse_args(args):
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage=usage) 

	parser.add_option('-m', action="store", type="string", dest="mapfile",help="Path/name of the map file", default="maps/lvl-1.txt")

	(opt, args) = parser.parse_args()
	return opt, args

def read_map(path):
	# read map as rows x columns
	map_data = []
	input_file = open(path, "r")
	for line in input_file:
		map_data.append([])
		for char in line[:-1]:
			map_data[-1].append(char)

	# instantiate map class as columns x rows
	map_struct = Map()
	for j in range(len(map_data[0])):
		for i in range(len(map_data)):
			map_struct.append(map_data[i][j])

	return map_struct

def run(path_to_map):


	# GENERATE A MAP-MATRIX STRUCTURE TO HOLD THE ORIGINAL MAP
	map_data = read_map(path_to_map)
	logger.info("Selected Map File: {}".format(path_to_map))
	logger.info("Rows: {}, Columns: {}".format(map_data.n_rows, map_data.n_cols))
	map_data.pretty_print()
	
	# SELECT N POINTS FROM THE MAP, WITH D DISTANCE FROM EACH OTHER
	N = 3
	D = 3
	selected_points = get_points(map_data, 3, 3)
	logger.info("Selected points: {}".format(selected_points))

	# SELECT SUBSTRUCTURES WITH D DISTANCE FROM CORE NODE PLUS 
	# S DISTANCE IF NEIGHBOURS ARE OF THE SAME TYPE AS CURRENT 
	D = 4
	S = 2
	# substructures, connecting_nodes = get_substructures(map_data, selected_points, D, S)
	# logger.info("Selected substructures:")
	# for c_id in substructures.keys():
	# 	logger.info(substructures[c_id])
	# logger.info("Connecting nodes:")
	# for c_id in substructures.keys():
	# 	for n in connecting_nodes[c_id]:
	# 		print("{}: {}, {}".format(c_id, n, n.edges))
	substructures = get_substructures(map_data, selected_points, D, S)

	# RELATIVIZE ALL CORDINATES SO THAT THE SMALLEST X START AT 0
	logger.info("Selected substructures:")
	for s in substructures:
		logger.info("Before relativization:")
		logger.info(s)
		s.relativize_coordinates()
		logger.info("After relativization:")
		logger.info(s)

	# #===== individual cluster log for debug ======
	# logger.info("Substructures without normalized columns: ")
	# for c_id in substructures.keys():
	# 	print("Cluster {}".format(c_id))
	# 	for n in substructures[c_id]:
	# 		print("{}, {}".format(n, n.edges))
	# 	print("Connecting nodes: ")
	# 	for n in connecting_nodes[c_id]:
	# 		print("{}, {}".format(n, n.edges))	
	# 	break

	# return

	# RELATIVIZE ALL CORDINATES SO THAT THE SMALLEST X START AT 0
	# for c_id in substructures.keys():
	# 	substructures[c_id] = relativize_coordinates(substructures[c_id])	
	# logger.info("Substructures with normalized columns: ")
	# for c_id in substructures.keys():
	# 	logger.info(substructures[c_id])
	# logger.info("Connecting nodes:")
	# for c_id in substructures.keys():
	# 	for n in connecting_nodes[c_id]:
	# 		print("{}: {}, {}".format(c_id, n, n.edges))

	# #===== individual cluster log for debug ======
	# logger.info("Substructures with normalized columns: ")
	# for c_id in substructures.keys():
	# 	print("Cluster {}".format(c_id))
	# 	for n in substructures[c_id]:
	# 		print("{}, {}".format(n, n.edges))
	# 	print("Connecting nodes: ")
	# 	for n in connecting_nodes[c_id]:
	# 		print("{}, {}".format(n, n.edges))
	# 	break


	# FIND POSSIBLE COMBINATIONS BETWEEN SUBSTRUCTURES
	find_substructures_combinations(substructures)
	logger.info("Checking identified combinable substructures: ")
	for s1 in substructures:
		logger.info("Substructure {} can be combined with: ".format(s1.id))
		for s2, n2 in s1.combinable:
			logger.info("{}, {}".format(s2.id, n2))

	# logger.info("Combinations found: ")
	# for c_id in connecting_nodes.keys():
	# 	connecting_nodes_list = connecting_nodes[c_id]
	# 	for connecting in connecting_nodes_list:

	# 		logger.info("Combinations for cluster {}, connection node {}:".format(c_id, connecting))
	# 		for connector in connecting.connectors:
	# 			logger.info("{}: {}".format(connector.cluster_id, connector))

	# for n in connecting_nodes:
		
	# 	for c in n.connectors:
	# 		logger.info("{}: {}".format(c.cluster_id, c))


if __name__ == '__main__':
	opt, args = parse_args(sys.argv[1:])	
	
	run(opt.mapfile)
	# logger.info("Selected Map File: {}".format(opt.mapfile))
	# map_data = read_map(opt.mapfile)
	# print(map_data.n_rows)
	# print(map_data.n_cols)
	
	# map_data.pretty_print()
	# selected_points = get_points(map_data, 3, 3)

	# print("Selected points: {}".format(selected_points))

	# substructures = get_substructures(map_data, selected_points)
	# print(substructures)
	


