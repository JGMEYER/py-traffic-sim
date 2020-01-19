from typing import List, Tuple

from .common import (
    TILE_WIDTH as tw,
    RoadNodeType,
    Update,
    Updateable,
    world_coords_to_grid_index,
)
from .grid import RoadSegmentNode
from physics import pathing


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
        x, y = v._world_coords
        self.vehicles.append(v)
        self.updates.append((Update.ADDED, (v._id, x, y)))
        return v

    def step(self, tick, grid, vehicle_stop_wait_time):
        """Step each vehicle in traffic list"""
        for v in self.vehicles:
            v.step(tick, grid, vehicle_stop_wait_time)

    def get_updates(self) -> List[Tuple[Update, Tuple[int, float, float]]]:
        """Get updates and clear updates queue"""
        updates = self.updates

        # For now, always assume a Vehicle has moved
        for v in self.vehicles:
            x, y = v._world_coords
            updates.append((Update.MODIFIED, (v._id, x, y)))

        self.updates = []
        return updates


class Vehicle():
    """A Vehicle that travels along the TravelGraph"""

    def __init__(self, id, node: RoadSegmentNode):
        # Attributes
        self._id = id
        self.speed = 1 * tw  # WARNING: could have undesirable behavior

        # Location
        self._world_coords = node.world_coords

        # Travel path
        self._path = []
        self._last_t_node = node  # last target node

        self._t_node = None  # target node
        self._trajectory = None

        # Intersection
        self.wait_time = 0  # sec

    def set_path(self, path: List[RoadSegmentNode]):
        """Set travel path for vehicle. This should be a list of nodes where
        any (path[i], path[i+1]) are connected nodes in a `TravelGraph`.
        """
        self._clear_target()
        self._path = path
        self._set_target()

    def _move_towards_target(self, trajectory, max_move_dist):
        """Attempt to move a vehicle a certain distance towards a target
        location.

        trajectory - trajectory
        target_x - target x world position
        target_y - target y world position
        max_move_dist - maximum distance vehicle can move towards target

        returns: distance moved
        """
        self._world_coords, moved_dist = trajectory.move(max_move_dist)
        return moved_dist

    def _has_target(self):
        """Vehicle has a target node and trajectory."""
        return self._t_node is not None and self._trajectory is not None

    def _clear_target(self):
        """Clear Vehicle target node and trajectory."""
        self._t_node = None  # target node
        self._trajectory = None

    def _set_target(self):
        """Set Vehicle target node and trajectory."""
        self._t_node = self._path[0]

        trajectory = pathing.LinearTrajectory(*self._world_coords,
                                              *self._t_node.world_coords)
        self._trajectory = trajectory

    def step(self, tick, grid, stop_wait_time):
        """Move a distance based on our speed towards the next node in our
        path, readjusting targets as needed in case we reach them mid-step.

        If a vehicle reaches an intersection, have it momentarily pause at a
        stop sign.
        """
        remaining_move_dist = self.speed * tick

        self.wait_time = max(self.wait_time - tick, 0)

        while self.wait_time == 0 and remaining_move_dist > 0:
            if not self._path:
                return

            if not self._has_target():
                self._set_target()

            # Attempt move towards target
            dist_moved = self._move_towards_target(self._trajectory,
                                                   remaining_move_dist)

            # Target reached
            if self._world_coords == self._t_node.world_coords:

                if self._t_node.node_type == RoadNodeType.ENTER:
                    r, c = world_coords_to_grid_index(
                                   *self._t_node.world_coords)

                    # Pause at stop sign
                    if grid.tile_type(r, c).is_intersection():
                        self.wait_time = stop_wait_time

                self._last_t_node = self._path.pop(0)

                if self._path:
                    self._set_target()
                else:
                    self._clear_target()

            remaining_move_dist -= dist_moved
