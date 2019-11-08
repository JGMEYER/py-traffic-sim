import numpy as np
from typing import List

from .constants import TILE_WIDTH as tw
from .grid import (
    road_segment_node_to_world_coords,
    RoadSegmentNode,
)


class Traffic():
    """A class for managing all vehicle traffic"""

    def __init__(self):
        self.vehicles = []

    def add_vehicle(self, node: RoadSegmentNode):
        """Add vehicle to traffic list"""
        self.vehicles.append(Vehicle(node))

    def step(self):
        """Step each vehicle in traffic list"""
        for v in self.vehicles:
            v.step()


class Vehicle():
    """A Vehicle that travels along the TravelGraph"""

    def __init__(self, node: RoadSegmentNode):
        # Attributes
        self.speed = 0.05 * tw  # WARNING: could have undesirable behavior
        # Location
        self.world_coords = road_segment_node_to_world_coords(node)
        # Travel path
        self.path = [node]  # always keep 1 in path
        self.last_node = node

    def set_path(self, path: List[RoadSegmentNode]):
        """Set travel path for vehicle. This should be a list of nodes where
        any (path[i], path[i+1]) are connected nodes in a `TravelGraph`."""
        self.path = path

    def move_towards(self, target_x, target_y, max_move_dist):
        """Move vehicle a certain distance towards a target location.

        If the vehicle would reach the destination in less than the provided
        distance, move the vehicle to the target position and return how much
        the vehicle moved to reach it.

        target_x - target x world position
        target_y - target y world position
        max_move_dist - maximum distance vehicle can move towards target

        returns: distance moved
        """
        my_x, my_y = self.world_coords
        vector = np.array([target_x - my_x, target_y - my_y])
        norm = np.linalg.norm(vector)

        # We reached our target
        if norm <= max_move_dist:
            self.world_coords = (target_x, target_y)
            return max_move_dist - norm

        unit = vector/norm
        self.world_coords = tuple(np.array(self.world_coords)
                                  + max_move_dist * np.array(unit))
        return max_move_dist

    def step(self):
        """Move a distance based on our speed towards the next node in our
        path, readjusting targets as needed in case we reach them mid-step.
        """
        remaining_move_dist = self.speed

        while remaining_move_dist > 0:
            if not self.path:
                return

            t_node = self.path[0]
            t_x, t_y = road_segment_node_to_world_coords(t_node)

            # Attempt move towards target
            dist_moved = self.move_towards(t_x, t_y, remaining_move_dist)

            # Target reached!
            if self.world_coords == (t_x, t_y):
                self.last_node = self.path.pop(0)

            remaining_move_dist -= dist_moved
