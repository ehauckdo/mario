#import map_matrix, grammar
import os
import sys
import optparse
import logging, inspect
import random

from map import Map, Generated_Map
from point_selection import get_points
from substructure_selection import get_substructures
from substructure_combine import find_substructures_combinations
from map_generation import instantiate_base_map

# set up logger
logging.basicConfig(filename="log", level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)

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

	# Generate a Map-Matrix structure to hold the original map
	map_data = read_map(path_to_map)
	logger.info("Selected Map File: {}".format(path_to_map))
	logger.info("Rows: {}, Columns: {}".format(map_data.n_rows, map_data.n_cols))
	logger.info(map_data.pretty_print())

	# Step 1	
	# Select N points from the map, with D distance from each other 
	N = 30
	#N = 2
	D = 4
	selected_points = get_points(map_data, N, D)
	logger.info("Selected points ({}): {}".format(N, selected_points))

	# Step 2
	# Select substructures expanding from previously selected points
	# Expansion will be done until D manhattan-distance from the core
	# points. If tiles around the edges are the same as of the edges,
	# this expansion can continue for more S manhattan-distance.
	D = 3
	S = 4
	substructures = get_substructures(map_data, selected_points, D, S)
	logger.info("Selected Substructures: ")
	for s in substructures:
		logger.info("\n{}".format(s.pretty_print(True)))

	# Relativize the node position of all structures, so that the 
	# left-most node start at column 0
	logger.info("Substructures after relativization:")
	for s in substructures:
		s.relativize_coordinates()
		logger.info("\n{}".format(s.pretty_print()))

	# Step 3
	# Instantiate starting and finishing substructures of the map
	# and add them to the list of substructures for the next step
	g_s, g_f = instantiate_base_map(len(substructures)+1)
	#logger.info("g_s: \n{}, \ng_f: \n{}".format(g_s.pretty_print(), g_f.pretty_print()))
	substructures.append(g_s)
	substructures.append(g_f)

	# Step 3
	# Find possible combinations between all substructures 
	find_substructures_combinations(substructures)
	logger.info("Checking identified combinable substructures: ")
	for s1 in substructures:
		logger.info("Substructure {} can be combined with: ".format(s1.id))
		for n in s1.connecting:
			logger.info("From node {}: {}".format(n, n.edges[0].properties["combinable"]))

	# remove starting and finishing structures from list, 
	# we don't want to use them during combination process
	substructures.remove(g_s)
	substructures.remove(g_f)

	import copy
	generated_structure = copy.deepcopy(g_s)
	logger.info("Initial structure generated! ")
	logger.info(generated_structure.pretty_print())

	available_substitutions = generated_structure.get_available_substitutions()
	count_substitutions = 0
	logger.info("Starting substitution process...")

	while len(available_substitutions) > 0:

		# TODO find a better way of selecting structures with
		# more than 1 connecting node
		while len(available_substitutions) > 0:
			c1, s_id, c2 = random.choice(available_substitutions)
			available_substitutions.remove((c1,s_id, c2))
			for s in substructures:
				if s.id == s_id:
					break
			if len(s.connecting) > 1 and generated_structure.collides(s, c1, c2):
				logger.info("Found substructure: {}".format(s.id))
				logger.info("Number of Connecting Nodes: {}".format(len(s.connecting)))
				logger.info(s.pretty_print())
				break

		generated_structure.expand(s, c1, c2)

		available_substitutions = generated_structure.get_available_substitutions()
		logger.info("Available substitutions: {}".format(len(available_substitutions)))
		logger.info("Count: {}".format(count_substitutions))
		logger.info("\n{}".format(generated_structure.pretty_print()))

		count_substitutions += 1

		if count_substitutions >= 15:
			for connecting in generated_structure.connecting:
				for s_id, n2 in connecting.edges[0].properties["combinable"]:
					if s_id == g_f.id:
						generated_structure.expand(g_f, connecting, n2)
						available_substitutions = []
						break

	generated_structure.save_as_map()


if __name__ == '__main__':
	opt, args = parse_args(sys.argv[1:])	
	sys.setrecursionlimit(10000) # required for some of the operations
	run(opt.mapfile)


