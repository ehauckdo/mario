#import map_matrix, grammar
import os
import sys
import optparse
import logging, inspect
import random

from .level import Level
from .point_selection import get_points
from .substructure_selection import get_substructures
from .substructure_combine import find_substructures_combinations
from .level_generation import instantiate_base_level

logger = logging.getLogger(__name__)

def read_level(path):
	# read map as rows x columns
	map_data = []
	input_file = open(path, "r")
	for line in input_file:
		map_data.append([])
		for char in line[:-1]:
			map_data[-1].append(char)

	# instantiate map class as columns x rows
	map_struct = Level()
	for j in range(len(map_data[0])):
		for i in range(len(map_data)):
			map_struct.append(map_data[i][j])

	return map_struct

def run(path_to_map, n_maps, n, d, s):

	################ DEBUG FOR REACHABILITY #################
	# substructures = []
	# g_s, g_f = instantiate_base_level(len(substructures)+1)
	# #logger.info("g_s: \n{}, \ng_f: \n{}".format(g_s.pretty_print(), g_f.pretty_print()))
	# substructures.append(g_s)
	# substructures.append(g_f)

	# find_substructures_combinations(substructures)
	# logger.info("Checking identified combinable substructures: ")
	# for s1 in substructures:
	# 	logger.info("Substructure {} can be combined with: ".format(s1.id))
	# 	for n in s1.connecting:
	# 		logger.info("From node {}: {}".format(n, n.edges[0].properties["combinable"]))
	# return
	############################################

	# Generate a Map-Matrix structure to hold the original map
	map_data = read_level(path_to_map)
	logger.info("Selected Map File: {}".format(path_to_map))
	logger.info("Rows: {}, Columns: {}".format(map_data.n_rows, map_data.n_cols))
	logger.info(map_data.pretty_print())

	# Step 1
	# Select N points from the map, with D distance from each other
	min_dist = 4
	selected_points = get_points(map_data, n, min_dist)
	logger.info("Selected points ({}): {}".format(n, selected_points))

	# Step 2
	# Select substructures expanding from previously selected points
	# Expansion will be done until D manhattan-distance from the core
	# points. If tiles around the edges are the same as of the edges,
	# this expansion can continue for more S manhattan-distance.
	substructures = get_substructures(map_data, selected_points, d, s)
	logger.info("Selected Substructures: ")
	for s in substructures:
		logger.info("\n{}".format(s.pretty_print(True)))

	# Relativize the node position of all structures, so that the
	# left-most node start at column 0
	logger.info("Substructures after relativization:")
	for s in substructures:
		s.relativize_coordinates()
		logger.info("\n{}".format(s.pretty_print_nodes()))

	# Step 3
	# Instantiate starting and finishing substructures of the map
	# and add them to the list of substructures for the next step
	g_s, g_f = instantiate_base_level(len(substructures)+1)
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

	output_file = open("output/output_substructures_stats.txt", "w")
	for s in substructures:
		s.relativize_coordinates()
		#logger.info("\n{}".format(s.pretty_print()))
		print("{}, {}, {}".format(s.id, len(s.connecting), len(s.get_available_substitutions())), file=output_file)
	output_file.close()

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

		generated_structure.save_as_level("output/levels/level_{}.txt".format(i))
