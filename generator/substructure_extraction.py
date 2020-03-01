import logging
from .level import Level
from .point_selection import spaced_selection, evenly_spaced_selection
from .substructure_selection import get_substructures

logger = logging.getLogger(__name__)

def read_level(path):
  logger.info("Reading {}".format(path))
  # read map as rows x columns
  map_data = []
  input_file = open(path, "r")
  for line in input_file:
    map_data.append([])
    for char in line:
      if char == "\n": continue
      map_data[-1].append(char)

  # instantiate map class as columns x rows
  map_struct = Level()
  for j in range(len(map_data[0])):
    for i in range(len(map_data)):
      map_struct.append(map_data[i][j])

  return map_struct

def extract_structures(path_to_map, n, d, step=5):
  # Generate a Map-Matrix structure to hold the original map
  map_data = read_level(path_to_map)
  logger.info("Selected Map File: {}".format(path_to_map))
  logger.info("Rows: {}, Columns: {}".format(map_data.n_rows, map_data.n_cols))
  logger.info(map_data.pretty_print())

  while True:
    # Step 1
    # Select N points from the map, with D distance from each other
    min_dist = 4
    selected_points = evenly_spaced_selection(map_data, n)
    #selected_points = spaced_selection(map_data, n, min_dist)
    logger.info("Selected points ({}): {}".format(n, selected_points))

    # Step 2
    # Select substructures expanding from previously selected points
    # Expansion will be done until D manhattan-distance from the core
    # points. If tiles around the edges are the same as of the edges,
    # this expansion can continue for more S manhattan-distance.
    substructures = get_substructures(map_data, selected_points, d)
    logger.info("Selected Substructures: ")
    for s in substructures:
        logger.info("\n{}".format(s.pretty_print(True)))

    connectors = []
    for s in substructures:
      connectors.append(len(s.connecting))
    average = sum(connectors)/len(connectors)
    if average < 2:
      n += step
    else:
      break

  # Relativize the node position of all structures, so that the
  # left-most node start at column 0
  logger.info("Substructures after relativization:")
  for s in substructures:
    s.relativize_coordinates()
    logger.info("\n{}".format(s.pretty_print()))

  return substructures
