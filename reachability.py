import logging
import math
import operator
logger = logging.getLogger(__name__)

# TODO: calculate reachability somehow
# def is_reachable(s1, s2):
# 	logger.info("Calculating Reachability...")

# 	newlist = sorted(s1.nodes, key=lambda x: x.r)
# 	logger.info("List of nodes from S1: ")

# 	logger.info(s1.pretty_print())

# 	platforms = []
# 	first = None

# 	for index in range(len(newlist)):
# 		n = newlist[index]
# 		if n.type != "Solid": continue

# 		if first == None:
# 			first = n
# 			continue

# 		if n.r != first.r:
# 			previous = newlist[index-1]
# 			platforms.append((first, previous))
# 			first = None

# 	if first != None:
# 		platforms.append((first, newlist[index-1]))

# 	for first, last in platforms:
# 		logger.info("{}, {}".format(first, last))

# 	return True

def getDistances(s1, s2):

	def dist(n1, n2):
		x = pow(n2.r - n1.r, 2)
		y = pow(n2.c - n1.c, 2)
		return math.sqrt(x+y)

	s1_solids = []
	s2_solids = []

	for n in s1.nodes: 
		if n.type == "Solid": s1_solids.append(n)
	for n in s2.nodes: 
		if n.type == "Solid": s2_solids.append(n)

	distances = []
	for n1 in s1_solids:
		for n2 in s2_solids:
			d = dist(n1, n2)
			distances.append((d, n1, n2))

	distances.sort(key=operator.itemgetter(0))
	return distances

def inside_triangle(n1, n2, dist):
	def area(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
		return abs((p1_x*(p2_y-p3_y) + p2_x*(p3_y-p1_y) 
										+ p3_x*(p1_y-p2_y))/2.0)
	p1_x = n1.c - dist 
	p1_y = n1.r
	p2_x = n1.c + dist
	p2_y = n1.r
	p3_x = n1.c
	p3_y = n1.r - dist

	A = area(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)
	A1 = area(n2.c, n2.r, p2_x, p2_y, p3_x, p3_y)
	A2 = area(p1_x, p1_y, n2.c, n2.r, p3_x, p3_y)
	A3 = area(p1_x, p1_y, p2_x, p2_y, n2.c, n2.r)
	return abs(A1 + A2 + A3 - A) <= 0.001

	return True

def is_reachable(s1, s2, dist=4):
	return True
	logger.info("Calculating Reachability...")

	distances = getDistances(s1, s2)

	for d, n1, n2 in distances:
		logger.info("dist: {}, n1: {}, n2: {}".format(d, n1, n2))

		if inside_triangle(n1, n2, dist) or inside_triangle(n2, n1, dist):
			return True
		else:
			logger.info("Not reachable!")
	return False

