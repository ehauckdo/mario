import optparse, sys, os
from metrics import level_parser
from metrics import metrics
# TODO error checking for input

def parse_args(args):
	usage = "usage: %prog [options]"
	parser = optparse.OptionParser(usage=usage)
	parser.add_option('-l', action="store", type="string", dest="level",help="Path/name of the level file", default="input_level.txt")
	parser.add_option('-f', action="store", type="string", dest="folder",help="Path/name of the level file", default=None)
	(opt, args) = parser.parse_args()
	return opt, args

if __name__ == '__main__':
	opt, args = parse_args(sys.argv[1:])

	# Parse level file names and paths
	if opt.folder != None:
		file_names = os.listdir(opt.folder)
		file_paths = ["{}{}".format(opt.folder,x) for x in file_names]
	else:
		file_names = file_paths = [opt.level]

	# Compute metrics for each level
	linearity, leniency = [], []
	for path in file_paths:
		level = level_parser.read_level(path)
		linearity.append(metrics.compute_linearity(level))
		leniency.append(metrics.compute_leniency(level))

	# Output results to a csv file
	output_file = open("result.csv", "w")
	print("level, linearity, leniency", file=output_file)
	for file, lin, len in zip(file_names, linearity, leniency):
		print("{}, {:.2f}, {:.2f}".format(file, lin,len), file=output_file)
		print("{}, {:.2f}, {:.2f}".format(file, lin,len))
	output_file.close()
