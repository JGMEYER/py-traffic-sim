from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class Trajectory(ABC):

    @abstractmethod
    def move(self, max_move_dist) -> (Tuple[float, float], float):
        """Move the point along the trajectory towards its target by the
        specified distance.

        If the point would reach the target in less than the provided move
        distance, move the point only to the target destination.

        max_move_dist - maximum distance point can move towards target

        returns: (new_x, new_y), distance_moved
        """
        pass


class LinearTrajectory(Trajectory):
    """Trajectory that moves a point linearly towards a target point."""

    def __init__(self, start_x, start_y, end_x, end_y):
        self._cur_x, self._cur_y = start_x, start_y
        self._end_x, self._end_y = end_x, end_y

    def move(self, max_move_dist) -> (Tuple[float, float], float):
        """See parent method for desc."""
        vector = np.array([self._end_x - self._cur_x,
                           self._end_y - self._cur_y])
        norm = np.linalg.norm(vector)

        # Target reached
        if max_move_dist >= norm:
            return (self._end_x, self._end_y), max_move_dist - norm

        unit = vector/norm
        self._cur_x, self._cur_y = tuple(np.array([self._cur_x, self._cur_y])
                                         + max_move_dist * np.array(unit))
        return (self._cur_x, self._cur_y), max_move_dist
