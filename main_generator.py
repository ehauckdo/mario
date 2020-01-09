import sys, os
import optparse
import logging
from pathlib import Path
from generator import generator
from generator import level_generation
from generator import substructure_extraction
from generator import substructure_combine

logging.basicConfig(filename="logs/log", level=logging.INFO, filemode='w')

def parse_args(args):
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage=usage)
	parser.add_option('-m', action="store", type="string", dest="mapfile",help="Path/name of the map file", default="maps/lvl-1.txt")
	parser.add_option('-o', action="store", type="int", dest="output_number",help="Number of maps to be generated", default=1)
	parser.add_option('-n', action="store", type="int", dest="n",help="Number of structures to be selected", default=30)
	parser.add_option('-d', action="store", type="int", dest="d",help="Minimum radius of structures", default=3)
	parser.add_option('-s', action="store", type="int", dest="s",help="Extended radius of structures based on similarity", default=8)

	(opt, args) = parser.parse_args()
	return opt, args

if __name__ == '__main__':
	opt, args = parse_args(sys.argv[1:])
	sys.setrecursionlimit(10000) # required for some of the operations

    # make sure the output directory exists, otherwise create it
	Path("output/structures/").mkdir(parents=True, exist_ok=True)

	# Randomnly select 'n' points from in the map
	# with a minimum of D size and extended size S
	substructures = substructure_extraction.extract_structures(opt.mapfile, opt.n, opt.d, opt.s)

	# Instiate the base starting and finishing structures
	g_s, g_f = level_generation.instantiate_base_level(len(substructures)+1)
	substructures.append(g_s)
	substructures.append(g_f)

	substructure_combine.find_substructures_combinations(substructures)

	substructures.remove(g_s)
	substructures.remove(g_f)

	output_file = open("output/output_substructures_stats.txt", "w")
	for s in substructures:
		print("{}, {}, {}".format(s.id, len(s.connecting), len(s.get_available_substitutions())), file=output_file)
	output_file.close()

	level_generation.generate_levels(substructures, g_s, g_f, opt.output_number)
