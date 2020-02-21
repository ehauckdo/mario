import logging
import math
import operator
logger = logging.getLogger(__name__)

# TODO: calculate reachability somehow
# def is_reachable(s1, s2):
#   logger.info("Calculating Reachability...")

#   newlist = sorted(s1.nodes, key=lambda x: x.r)
#   logger.info("List of nodes from S1: ")

#   logger.info(s1.pretty_print())

#   platforms = []
#   first = None

#   for index in range(len(newlist)):
#     n = newlist[index]
#     if n.type != "Solid": continue

#     if first == None:
#       first = n
#       continue

#     if n.r != first.r:
#       previous = newlist[index-1]
#       platforms.append((first, previous))
#       first = None

#   if first != None:
#     platforms.append((first, newlist[index-1]))

#   for first, last in platforms:
#     logger.info("{}, {}".format(first, last))

#   return True

def computeReachability(n1, n2):

  def inside_triangle(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, x, y):

    def area(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
      return abs((p1_x*(p2_y-p3_y) + p2_x*(p3_y-p1_y)
                    + p3_x*(p1_y-p2_y))/2.0)

    A = area(p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)
    A1 = area(x, y, p2_x, p2_y, p3_x, p3_y)
    A2 = area(p1_x, p1_y, x, y, p3_x, p3_y)
    A3 = area(p1_x, p1_y, p2_x, p2_y, x, y)
    return abs(A1 + A2 + A3 - A) <= 0.001

  def inside_rectangle(left_x, right_x, bottom_y, top_y, x, y):
    if x >= left_x and x <= right_x and y <= bottom_y and y >= top_y:
      return True
    else: return False

  logger.debug("Calculating Rectangle and Triangles from node {}...".format(n1))
  h_dist = 3
  v_dist = 4

  rect_c_min = 0 if n1.c - h_dist < 0 else n1.c - h_dist
  rect_c_max = n1.c + h_dist
  rect_r_min = 0 if n1.r - v_dist < 0 else n1.r - v_dist
  rect_r_max = 15 if n1.r + v_dist > 15 else n1.r + v_dist

  logger.debug("c_min: {}, c_max: {}".format(rect_c_min, rect_c_max))
  logger.debug("r_min: {}, r_max: {}".format(rect_r_min, rect_r_max))

  t1_p1_c = rect_c_min
  t1_p1_r = rect_r_min

  t1_p2_c = rect_c_min
  t1_p2_r = 15

  # loose approximation
  t1_p3_c = rect_c_min - (15-rect_r_min)/2
  if t1_p3_c < 0: t1_p3_c = 0
  t1_p3_r = 15

  logger.debug("t1 p1: ({},{}), p2: ({},{}), p3: ({},{}),".format(t1_p1_r,t1_p1_c,  t1_p2_r, t1_p2_c, t1_p3_r, t1_p3_c))

  t2_p1_c = rect_c_max
  t2_p1_r = rect_r_min

  t2_p2_c = rect_c_max
  t2_p2_r = 15

  # loose approximation
  t2_p3_c = rect_c_max + int((15-rect_r_min)/2)
  t2_p3_r = 15

  # logger.info("Difference x: {}, difference y: {}".format(difference_x, difference_y))
  # angle = math.degrees(math.atan2(difference_x, difference_y))
  # logger.info("atan: {}".format(angle))

  logger.info("t2 p1: ({},{}), p2: ({},{}), p3: ({},{}),".format(t2_p1_r,t2_p1_c, t2_p2_r, t2_p2_c, t2_p3_r, t2_p3_c))

  triang1 = inside_triangle(t1_p1_c, t1_p1_r, t1_p2_c, t1_p2_r, t1_p3_c, t1_p3_r, n2.c, n2.r)
  logger.info("Checking if inside triangle 1: {}".format(triang1))

  triang2 = inside_triangle(t2_p1_c, t2_p1_r, t2_p2_c, t2_p2_r, t2_p3_c, t2_p3_r, n2.c, n2.r)
  logger.info("Checking if inside triangle 2: {}".format(triang2))

  rect = inside_rectangle(rect_c_min, rect_c_max, rect_r_max, rect_r_min, n2.c, n2.r)
  logger.info("Checking if inside rectangle: {}".format(rect))

  return triang1 or triang2 or rect

def getDistances(s1, s2):

  def dist(n1, n2):
    x = pow(n2.r - n1.r, 2)
    y = pow(n2.c - n1.c, 2)
    return math.sqrt(x+y)

  s1_solids = []
  s2_solids = []
  s2_nonsolids = []

  for n in s1.nodes:
    if n.type == "Solid": s1_solids.append(n)
  for n in s2.nodes:
    if n.type == "Solid": s2_solids.append(n)
    elif n.type == "Non-Solid": s2_nonsolids.append(n)


  logger.info("s1 solids: {}".format(s1_solids))
  logger.info("s2 solids: {}".format(s2_solids))

  distances = []
  for n1 in s1_solids:
    for n2 in s2_solids+s2_nonsolids:
      d = dist(n1, n2)
      distances.append((d, n1, n2))

  distances.sort(key=operator.itemgetter(0))

  return distances


def is_reachable(s1, s2, dist=4.5):
  logger.info("Calculating Reachability...")
  logger.info("S1: \n{}".format(s1.pretty_print()))
  logger.info("S2: \n{}".format(s2.pretty_print()))

  distances = getDistances(s1, s2)

  for d, n1, n2 in distances:
    logger.info("dist: {}, n1: {}, n2: {}".format(d, n1, n2))

    if computeReachability(n1, n2):
      logger.info("Reachable!")
      return True
    else:
      logger.info("Not reachable!")
  return False
