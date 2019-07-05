import sys
from metrics import calculateLeniency
import os, logging

def readMaps(folder):
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

def printMap(map):

	for line in map:
		string = ""
		for char in line:
			string += char
		print(string)

maps = readMaps("mapsNotchDif4")
for key, value in maps.items():
	#print(key)
	print(calculateLeniency(maps[key]))
	

calculateLeniency(maps["map9.txt"])

	






