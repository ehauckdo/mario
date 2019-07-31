import sys
import metrics
import os, logging

def read_maps(folder):
	map_files = os.listdir(folder)
	maps = {}

	for m in map_files:
		logging.info("Parsing {}".format(m))
		map = []
		input_file = open(folder+"/"+m, "r")
		for line in input_file:
			map.append([])
			for char in line:
				map[-1].append(char)
	
		maps[m] = map[:-1]

	return maps

def normalize(number_list):
	amin, amax = min(number_list), max(number_list)
	print(amin, amax)
	
	for i, val in enumerate(number_list):
		number_list[i] = (val-amin) / (amax-amin)


maps = read_maps("data/mapsNotchDif4")

# calculate the leniency for all the maps found
leniency = []
for key, value in maps.items():
	leniency.append(metrics.calculate_leniency(maps[key]))

# normalize and print leniency values
normalize(leniency)
for l in leniency:
	print(l)

	






