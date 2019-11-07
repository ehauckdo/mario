#import map_matrix, grammar
import os
import sys
import optparse
import math
import logging, inspect

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
		index = self.n_rows * y + x
		return self.map_data[index]

	def map_pretty_print(self):
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

def get_points(map_data):
	n_cols = map_data.n_cols
	n_rows = map_data.n_rows
	print(n_cols, n_rows)

if __name__ == '__main__':
	opt, args = parse_args(sys.argv[1:])	
	
	logger.info("Selected Map File: {}".format(opt.mapfile))

	map_data = read_map(opt.mapfile)
	print(map_data.n_rows)
	print(map_data.n_cols)
	
	map_data.map_pretty_print()
	get_points(map_data)
	

