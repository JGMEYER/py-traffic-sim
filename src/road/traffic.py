import numpy as np
from typing import List, Tuple

from .constants import TILE_WIDTH as tw, Update, Updateable
from .grid import RoadSegmentNode


class Traffic(Updateable):
    """A class for managing all vehicle traffic"""

    # Counter to track next vehicle id
    vehicle_ids = -1

    def __init__(self):
        self.vehicles = []
        self.updates = []

    def add_vehicle(self, node: RoadSegmentNode):
        """Add vehicle to traffic list"""
        id = self.vehicle_ids = self.vehicle_ids + 1
        v = Vehicle(id, node)
        x, y = v.world_coords
        self.vehicles.append(v)
        self.updates.append((Update.ADDED, (v.id, x, y)))
        return v

    def step(self, tick):
        """Step each vehicle in traffic list"""
        for v in self.vehicles:
            v.step(tick)

    def get_updates(self) -> List[Tuple[Update, Tuple[int, float, float]]]:
        """Get updates and clear updates queue"""
        updates = self.updates

        # For now, always assume a Vehicle has moved
        for v in self.vehicles:
            x, y = v.world_coords
            updates.append((Update.MODIFIED, (v.id, x, y)))

        self.updates = []
        return updates


class Vehicle():
    """A Vehicle that travels along the TravelGraph"""

    def __init__(self, id, node: RoadSegmentNode):
        # Attributes
        self.id = id
        self.speed = 1 * tw  # WARNING: could have undesirable behavior

        # Location
        self.world_coords = node.world_coords

        # Travel path
        self.path = []
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
        if max_move_dist >= norm:
            self.world_coords = (target_x, target_y)
            return max_move_dist - norm

        unit = vector/norm
        self.world_coords = tuple(np.array(self.world_coords)
                                  + max_move_dist * np.array(unit))
        return max_move_dist

    def step(self, tick):
        """Move a distance based on our speed towards the next node in our
        path, readjusting targets as needed in case we reach them mid-step.
        """
        remaining_move_dist = self.speed * tick

        while remaining_move_dist > 0:
            if not self.path:
                return

            t_node = self.path[0]
            t_x, t_y = t_node.world_coords

            # Attempt move towards target
            dist_moved = self.move_towards(t_x, t_y, remaining_move_dist)

            # Target reached!
            if self.world_coords == (t_x, t_y):
                self.last_node = self.path.pop(0)

            remaining_move_dist -= dist_moved
