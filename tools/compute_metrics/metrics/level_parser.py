import sys, os
from pathlib import Path
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

def normalize(number_list):
	logger.debug(" (CALL) {}".format(inspect.stack()[0][3]))
	amin, amax = min(number_list), max(number_list)
	print(amin, amax)

	for i, val in enumerate(number_list):
		number_list[i] = (val-amin) / (amax-amin)
	logger.debug(" (RTRN) {}".format(inspect.stack()[0][3]))
