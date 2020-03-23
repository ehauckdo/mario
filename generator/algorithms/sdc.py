# Author: Georgy Skorobogatov (LostFan123)
# https://gist.github.com/LostFan123/63c7a1a26945ffaf115dc6886b69e862
# Implementation of the Supression via Disk Covering for
# selection spatially distributed points on an image
from functools import partial
from typing import Tuple

import numpy as np

def select(points: np.ndarray,
           *,
           image_shape: Tuple[int, int],
           count: int,
           count_delta: int = 1,
           radius: int = 10,
           radius_delta: int = 0.01,
           max_iterations_count: int = 1000,
           min_cell_size: int = 2,
           max_cell_size: int = 100) -> np.ndarray:
    """
    Selects points by a Suppression via Disk Covering algorithm.
    For more details see:
    http://lucafoschini.com/papers/Efficiently_ICIP11.pdf
    :param points: original set that should be ordered by distance
    :param image_shape: shape of an image
    :param count: number of output points
    :param count_delta: let k = `count` and Δk = `count_delta`,
    if number of found points is within [k; k + Δk],
    return top-k points
    :param radius: initial radius of area where points will be removed
    :param radius_delta: determines width of cells
    :param max_iterations_count: prevents infinite loop
    :param min_cell_size:
    :param max_cell_size:
    :return: mask array with selected strong scattered keypoints
    """
    if len(points) < count:
        raise ValueError('Not enough points to select.')

    grid_resolution = radius_delta * radius / np.sqrt(2)

    max_count = count + count_delta

    points_mask = partial(selected_points_mask,
                          points,
                          image_shape=image_shape,
                          count=max_count,
                          radius=radius)

    for _ in range(max_iterations_count):
        result_mask = points_mask(grid_resolution=grid_resolution)

        selected_points_count = result_mask.sum()

        if selected_points_count == count:
            return result_mask

        if count < selected_points_count <= max_count:
            return erase_extra_points(result_mask,
                                      count=count)

        if selected_points_count < count:
            max_cell_size = grid_resolution
            grid_resolution -= (grid_resolution - min_cell_size) / 2
        else:
            min_cell_size = grid_resolution
            grid_resolution += (max_cell_size - grid_resolution) / 2

    raise ValueError('Number of iterations exceeded.')


def selected_points_mask(points: np.ndarray,
                         *,
                         grid_resolution: float,
                         image_shape: Tuple[int, int],
                         count: int,
                         radius: int) -> np.ndarray:
    """
    Calculates boolean mask corresponding to array of input points.
    True values are for those points
    that will be selected as scattered enough from each other.
    In case if there were too many points found,
    the mask still will be returned.
    :param points: input array
    :param grid_resolution: size of a cell in a grid
    :param image_shape:
    :param count: number of points to select
    :param radius: as number of cells where points won't be selected
    :return: boolean array with True values for selected points
    """
    points_grid_indices = (points // grid_resolution).astype(int)

    grid_shape = (int(image_shape[0] // grid_resolution) + 1,
                  int(image_shape[1] // grid_resolution) + 1)
    grid = np.full(shape=grid_shape,
                   fill_value=False)

    result_mask = np.full(shape=points.shape[0],
                          fill_value=False)

    for index, point_grid_index in enumerate(points_grid_indices):
        if grid[tuple(point_grid_index)]:
            continue

        result_mask[index] = True

        if result_mask.sum() > count:
            break

        mask = circular_mask(grid.shape,
                             center=point_grid_index,
                             radius=radius)
        grid[mask] = True

    return result_mask


def circular_mask(array_shape: Tuple[int, int],
                  *,
                  center: Tuple[int, int],
                  radius: int) -> np.ndarray:
    """
    Returns 2d array with applied a disc shaped mask over it.
    For more details see:
    https://stackoverflow.com/questions/8647024/how-to-apply-a-disc-shaped-mask-to-a-numpy-array
    https://stackoverflow.com/questions/44865023/circular-masking-an-image-in-python-using-numpy-arrays
    :param array_shape: shape of original image
    :param center: center of the disc
    :param radius: radius of the disc
    :return: boolean array with applied circular mask
    """
    y, x = np.ogrid[-center[0]:array_shape[0] - center[0],
                    -center[1]:array_shape[1] - center[1]]
    return x * x + y * y <= radius * radius


def erase_extra_points(array: np.ndarray,
                       *,
                       count: int) -> np.ndarray:
    """
    Let n = `count`, sets to False all elements
    after the n-th occurrence of a True element.
    :param array: input boolean array
    :param count: number of True elements to remain
    :return:
    """
    array = array.copy()
    last_true_index_to_remain = np.where(array)[0][count]
    array[last_true_index_to_remain:] = False
    return array
