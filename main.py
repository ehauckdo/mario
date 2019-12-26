import sys, os
import optparse
import logging
from generator import generator

# set up logger
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
	output_directory = "output/"
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)

	generator.run(opt.mapfile, opt.output_number, opt.n, opt.d, opt.s)
