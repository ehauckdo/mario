import sys, os
import optparse
import logging
from pathlib import Path
from generator import level_generation
from generator import substructure_extraction
from generator import substructure_combine
from helper import io
from tools.render_level.render_level import render_structure

logging.basicConfig(filename="logs/log", level=logging.INFO, filemode='w')

def parse_args(args):
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage=usage)
	parser.add_option('-l', action="store", type="string", dest="mapfile",help="Path/name of the level file", default="maps/lvl-1.txt")
	parser.add_option('-o', action="store", type="int", dest="output_number",help="Number of level to be generated", default=1)
	parser.add_option('-n', action="store", type="int", dest="n",help="Number of structures to be selected", default=30)
	parser.add_option('-d', action="store", type="int", dest="d",help="Minimum radius of structures", default=3)
	parser.add_option('-s', action="store", type="int", dest="s",help="Extended radius of structures based on similarity", default=8)
	parser.add_option('-m', action="store", type="int", dest="min_structures",help="Minimum number of structures to be placed on a level", default=15)

	(opt, args) = parser.parse_args()
	return opt, args

def load_structures(path="output/structures"):
	structures = []
	g_s = None
	g_f = None

	for file in os.listdir(path):
		if "." not in file:
			if file == "g_s":
				g_s = io.load("{}/{}".format(path, file))
			elif file == "g_f":
				g_f = io.load("{}/{}".format(path, file))
			else:
				structure = io.load("{}/{}".format(path, file))
				structures.append(structure)

	return g_s, g_f, structures

def fetch_structures(opt):
	# Randomnly select 'n' points from in the map
	# with a minimum of D size and extended size S
	substructures = substructure_extraction.extract_structures(opt.mapfile, opt.n, opt.d, opt.s)

	# Instiate the base starting and finishing structures
	g_s, g_f = level_generation.instantiate_base_level(len(substructures)+1)

	substructure_combine.find_substructures_combinations(substructures + [g_s, g_f])

	for s in substructures+ [g_s, g_f]:
		io.save(s, "output/structures/s_{}".format(s.id))
		render_structure(s.matrix_representation(), "output/structures/s_{}.png".format(s.id))

	output_file = open("output/levels/level_stats.txt", "w")
	for s in substructures:
		print("{}, {}, {}".format(s.id, len(s.connecting), len(s.get_available_substitutions())), file=output_file)
	output_file.close()

	return g_s, g_f, substructures

if __name__ == '__main__':

	opt, args = parse_args(sys.argv[1:])
	sys.setrecursionlimit(10000) # required for some of the operations

	# make sure the output directory exists, otherwise create it
	Path("output/structures/").mkdir(parents=True, exist_ok=True)
	Path("output/levels/").mkdir(parents=True, exist_ok=True)

	g_s, g_f, substructures = load_structures()
	#g_s, g_f, substructures = fetch_structures(opt)

	for n in range(opt.output_number):
		structures_used = 0
		while structures_used < opt.min_structures:
			level, stats, structures_used = level_generation.generate_level(substructures, g_s, g_f, opt.min_structures)
		level_path = "output/levels/level_{}.txt".format(n)
		print("Rendering level {}".format(n))
		level.save_as_level(level_path)
		render_structure(level_path, "output/levels/level_{}.png".format(n))
