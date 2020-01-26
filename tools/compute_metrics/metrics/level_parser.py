import sys, os
from pathlib import Path
from .metrics import calculate_leniency
import logging, inspect

logger = logging.getLogger(__name__)

def read_level(file):
	logger.info("Parsing {}".format(file))
	map = []
	input_file = open(file, "r")
	for line in input_file:
		row = []
		for char in line:
			row.append(char)
		map.append(row)
	return map

def read_folder(folder):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	map_files = os.listdir(folder)
	maps = {}

	for m in map_files:
		maps[m] = read_level(folder+"/"+m)

	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
	return maps

def normalize(number_list):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	amin, amax = min(number_list), max(number_list)
	print(amin, amax)

	for i, val in enumerate(number_list):
		number_list[i] = (val-amin) / (amax-amin)
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))

def compute_metrics(maps_folder=str(Path(__file__).parent)+"/data/MapsNotchDif4/"):
	maps = read_folder(maps_folder)

	# calculate the leniency for all the maps found
	leniency = []
	for key, value in maps.items():
		leniency.append(calculate_leniency(maps[key]))

	# normalize and print leniency values
	normalize(leniency)
	for l in leniency:
		print(l)
