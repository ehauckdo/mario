import logging
import random
import copy
import sys
from . import constants
from .scoring import get_density_score, get_increasing_density_score
from .structure import Structure, Node, Connector
from .level import Level

logger = logging.getLogger(__name__)

def print_level(structures):
  directions = {"r":">", "l":"<", "u":"^", "d":"v"}
  level = Level()
  base_structure = Structure(-1)

  for s in structures:
    base_structure.nodes.extend(s.nodes)
    base_structure.connecting.extend(s.connecting)
  return base_structure.pretty_print()

def backtrack(structures):
  removed_structure = structures.pop()

  for connector in removed_structure.connecting:
    logger.info("Clearing connectors associated with structure {}".format(removed_structure.id))
    if connector.combined != None:
      structure1, c1 = connector.combined
      c1.combined = None
      logger.info("Clearing node {} from structure {}".format(c1.sub_id, structure1.id))
  return structures

def check_connectors(structures):
  """
    Experimental function
    Disable connectors that don't have sufficient space around them
  """
  level_matrix = {}
  for str in structures:
    for n in str.nodes:
      if (n.r, n.c) not in level_matrix.keys():
        level_matrix[(n.r,n.c)] = n.tile

  # list of adjacent tiles to check
  switcher = {
      "r": [(0, 0), (1,  0), (-1, 0), ( 0, 1), ( 1,  1), (-1,  1)],
      "l": [(0, 0), (1,  0), (-1, 0), ( 0,-1), ( 1, -1), (-1, -1)],
      "u": [(0, 0), (0, -1), ( 0, 1), (-1, 0), (-1, -1), (-1,  1)],
      "d": [(0, 0), (0, -1), ( 0, 1), ( 1, 0), ( 1, -1), ( 1,  1)]
  }

  for str in structures:
    for c in reversed(str.connecting):
      if c.combined == None:
        for r_d, c_d in switcher[c.direction]:
          # we check if there are tiles in the adjacent positions
          if (c.r + r_d, c.c + c_d) in level_matrix.keys():
            logger.info("disabling connector at ({},{})".format(c.r, c.c))
            #c.combined = -1
            str.connecting.remove(c)
            break

def prepare(structure1, c1, structure2, c2):
  """
    Prepare structure2 to to be connected with structure1
    1 - Adjust coordinates of all nodes
    2 - Set conectors as combined
    3 - Remove combinables from list of connectors
    4 - Remove nodes outside of screen bounds
  """
  horizontal = {"r": -1, "l": 1, "u": 0, "d": 0}
  vertical = {"r": 0, "l": 0, "u": -1, "d": 1}

  adjust_column = (c1.c + (horizontal[c1.direction])) - c2.c
  adjust_row = (c1.r + (vertical[c2.direction])) - c2.r

  c1.combined = [structure2, c2]
  c2.combined = [structure1, c1]

  c1.combinable.remove((structure2.id, c2.sub_id))
  c2.combinable.remove((structure1.id, c1.sub_id))

  for n in structure2.nodes+structure2.connecting:
    n.c += adjust_column
    n.r += adjust_row

  for n in reversed(structure2.nodes+structure2.connecting):
    if n.r < 0 or n.r > 15 or n.c < 0:
      try:
        structure2.nodes.remove(n)
      except:
        structure2.connecting.remove(n)
  return structure2

def has_collision(structures, ignore_air=True):
  """Given a list of structures, any tiles collide"""
  level_matrix = {}
  for str in structures:
    for n in str.nodes:
      if (n.r, n.c) not in level_matrix.keys():
        level_matrix[(n.r,n.c)] = n.tile
      else:
        if(not ignore_air) and (n.tile == "-"
            or level_matrix[(n.r,n.c)] == "-"):
          return True
  return False

def available_substitutions(structures):
  available =[]
  for str in structures:
    available.extend(str.available_substitutions())

  return available

def list_to_dict(structures, g_s, g_f):
  dict_structures = {}
  for s in structures+[g_s,g_f]:
    dict_structures[s.id] = s
  return dict_structures

def greed_search(g_s, g_f, structures):
  logger.info("starting BFS")
  original_structures = list_to_dict(structures, g_s, g_f)

  queue = [(get_density_score([g_s]), [g_s])]

  while len(queue) > 0:
    density, current = queue.pop(0)

    if len(current) == 30:
      logger.info("Finished generation")
      logger.info("Level: \n{}". format(print_level(current)))
      generated_structure = Structure(-1)
      #print("Length: {}".format(len(level)))
      for s in current:
        generated_structure.nodes.extend(s.nodes)
      return generated_structure, len(current)
      #sys.exit()

    substitutions = available_substitutions(current)

    for i in range(len(substitutions)):
      level = copy.deepcopy(current)
      str1, c1, str2_id, c2_sub_id = available_substitutions(level)[i]

      if str2_id == g_s.id or str2_id == g_f.id:
          continue

      str2 = copy.deepcopy(original_structures[str2_id])
      c2 = str2.get_connector(c2_sub_id)

      str2 = prepare(str1, c1, str2, c2)
      level.append(str2)

      check_connectors(level)
      collides = has_collision(level)
      substitutions = available_substitutions(level)

      if len(substitutions) <= 0 or collides:
        continue

      logger.info("saving expansion {}".format(i))

      queue.append((get_density_score(level), level))

    queue.sort(key=lambda x: x[0])
    logger.info("Sorted queue:")
    for density, level in queue:
      logger.info("Score {}". format(density))
      logger.info("Level: \n{}". format(print_level(level)))
    queue = queue[:1]
  return None, -1

def generate_level(structures, g_s, g_f, minimum_count=10):

  original_structures = list_to_dict(structures, g_s, g_f)
  usage_stats = dict.fromkeys(original_structures.keys(), 0)

  count_substitutions = 0
  count_backtrack = 0
  highest_col = 0
  finished = False

  logger.info("Generating level...")
  level = [] # the generating level is a list of structures
  level.append(copy.deepcopy(g_s))
  logger.info("Initial structure generated!\n{}". format(print_level(level)))

  substitutions = available_substitutions(level)

  logger.info("Starting substitution process...")
  logger.info("Available subsistutions: {}".format(len(substitutions)))

  while len(substitutions) > 0:

    while True:
      # logger.info("All Available substitutions: ")
      # for str1, c1, str2_id, c2_id in substitutions:
      #   logger.info("Structure {}, connector {}, to Structure {} via connector {}".format(str1.id, c1, str2_id, c2_id))
      while len(substitutions) == 0:
        level = backtrack(level)
        substitutions = available_substitutions(level)
        count_backtrack += 1
      str1, c1, str2_id, c2_sub_id = random.choice(substitutions)
      substitutions.remove((str1, c1, str2_id, c2_sub_id))
      if str2_id == g_s.id or str2_id == g_f.id: continue
      str2 =  copy.deepcopy(original_structures[str2_id])
      c2 = str2.get_connector(c2_sub_id)

      #logger.info("Trying to append structure {} using its connector {} via structure {} with connector {}".format(str2_id, c2, str1.id, c1))
      #logger.info("\n{}".format(str2.pretty_print()))

      str2 = prepare(str1, c1, str2, c2)
      level.append(str2)

      check_connectors(level)
      collides = has_collision(level, True)
      substitutions = available_substitutions(level)
      #density = get_density_score(level, 2)

      if len(substitutions) <= 0 or collides:
        if len(substitutions) <= 0: logger.info("Simulated structure has no available substitutions, trying next...")
        if collides: logger.info("Collision Happened!")
        c1.combined = None # reset state of first connector
        level = backtrack(level)
        substitutions = available_substitutions(level)
        #input("Press Enter to continue...")
      else:
        #logger.info("Sucessfull substitution")
        #input("Press Enter to continue...")
        usage_stats[str2_id] += 1
        for n in str2.nodes:
          if n.c > highest_col:
            highest_col = n.c
        break

    count_substitutions += 1
    if count_backtrack > 500:
      break

    logger.info("Available substitutions: {}".format(len(substitutions)))
    logger.info("Substitutions applied so far: {}".format(count_substitutions))
    logger.info("\n{}".format(print_level(level)))

    #if highest_col >= 202:
    if len(level) == minimum_count:
      # OPTION 1: try to append g_f
      # for str1, c1, str2_id, c2_sub_id in substitutions:
      #   if str2_id == g_f.id:
      #     str2 = copy.deepcopy(g_f)
      #     c2 = str2.get_connector(c2_sub_id)
      #     logger.info("Trying to append g_f {} using its connector {} via structure {} with connector {}".format(g_f.id, c2, str1.id, c1))
      #     str2 = prepare(str1, c1, str2, c2)
      #     #if not has_collision(level+[str2]):
      #     level.append(str2)
      #     logger.info("g_f finished!")
      #     usage_stats[str2_id] += 1
      #     print("Reached column 202!")
      #     finished = True
      #     break
      #
      # OPTION 2: simply cut off the level at 202
      for struct in level:
        for n in reversed(struct.nodes):
          if n.c > 201:
            struct.nodes.remove(n)
      finished = True
      break

    if finished:
      break

  generated_structure = Structure(-1)
  print("Length: {}".format(len(level)))
  for s in level:
    generated_structure.nodes.extend(s.nodes)
  return generated_structure, usage_stats, count_substitutions

def instantiate_base_level(id_structures):
  g_s = Structure(id_structures)
  for c in range(3):
    platform = Node(15, c, "X", "Solid", g_s)
    g_s.append_node(platform)
    platform = Node(14, c, "X", "Solid", g_s)
    g_s.append_node(platform)

    for r in range(14):
      if r == 13 and c == 1: continue
      air = Node(r, c, "-", "Non-Solid", g_s)
      g_s.append_node(air)

  mario = Node(13, 1, "M", "Solid", g_s)
  g_s.append_node(mario)

  connector = Connector(15, 3, "r", g_s)
  g_s.append_connector(connector)

  id_structures += 1
  g_f = Structure(id_structures)

  for c in range(1, 3):
    platform = Node(15, c, "X", "Solid", g_f)
    g_f.append_node(platform)
    platform = Node(14, c, "X", "Solid", g_f)
    g_f.append_node(platform)

    for r in range(14):
      if r == 13 and c == 2: continue
      air = Node(r, c, "-", "Non-Solid", g_f)
      g_f.append_node(air)

  finish = Node(13, 2, "F", "Solid", g_f)
  g_f.append_node(finish)
  connector = Connector(15, 0, "l", g_f)
  g_f.append_connector(connector)

  return g_s, g_f
