import logging
from .level import Level
from . import constants
logger = logging.getLogger(__name__)

def get_intervals(number, inter, skip=0):
  """Given an integer and a value for interval, return a list of
  tuples containing intervals within the 0-number range.
  e.g. 15 --> [(0,4),(5,9), (10,14)]
  """
  intervals = []
  inter_start = skip

  for i in range(number+1):
    if i - inter_start  == inter:
      intervals.append((inter_start, i-1))
      inter_start = i

  if i - inter_start > 0:
    intervals.append((inter_start, i-1))

  return intervals

def get_enemy_density(level, start_col=0, end_col=0):
  end_col = level.n_cols if (end_col == 0) else end_col
  enemies = 0
  for c in range(start_col, end_col+1):
    for r in range(level.n_rows):
      if level.get(r,c) in constants.enemy_tiles:
        enemies += 1
  return enemies

def create_level(structures):
  level = Level()
  for str in structures:
    for n in str.nodes:
      level.set(n.r, n.c, n.tile)
  return level

def get_density_score(structures, d=3, l=14):
  logger.info("Calculating density...")
  level = create_level(structures)

  # get intervals representing scenes, eg. 3-17, 18-34n
  intervals = get_intervals(level.n_cols, l, 3)
  logger.info("Number of columns: {}".format(level.n_cols))
  logger.info("Scenes in the level: \n{}".format(intervals))

  enemies = []
  for start_col, end_col in intervals:
    enemies.append(get_enemy_density(level, start_col, end_col))

  logger.info("Enemies on each interval: \n{}".format(enemies))
  enemies = [(abs(i-d)) for i in enemies]
  score = sum(enemies)
  logger.info("Score: {}".format(score))
  return score
  logger.info("Enemies found on each interval: \n{}".format(enemies))

def get_increasing_density_score(structures, d=2, l=14):
  logger.info("Calculating density...")
  level = create_level(structures)

  # get intervals representing scenes, eg. 3-17, 18-34n
  intervals = get_intervals(level.n_cols, l, 3)
  logger.info("Number of columns: {}".format(level.n_cols))
  logger.info("Scenes in the level: \n{}".format(intervals))

  enemies = []
  for start_col, end_col in intervals:
    enemies.append(get_enemy_density(level, start_col, end_col))

  logger.info("Enemies on each interval: \n{}".format(enemies))
  enemies = [(abs(n-(d*i))) for i, n in zip(range(len(enemies)), enemies)]
  logger.info("After processing: \n{}".format(enemies))
  score = sum(enemies)
  logger.info("Score: {}".format(score))
  return score
  logger.info("Enemies found on each interval: \n{}".format(enemies))
