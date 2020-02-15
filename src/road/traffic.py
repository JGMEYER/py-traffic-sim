from collections import deque
from typing import Dict, List, Tuple

from .common import (
    Direction,
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

    def __init__(self, config):
        self.config = config

        self.vehicles = []
        self.updates = []
        self.inscts: Dict(Tuple(int, int), Intersection) = {}  # (r, c): insct

    def add_vehicle(self, node: RoadSegmentNode):
        """Add vehicle to traffic list"""
        id = self.vehicle_ids = self.vehicle_ids + 1
        v = Vehicle(self.config, id, node)
        x, y = v._world_coords
        self.vehicles.append(v)
        self.updates.append((Update.ADDED, (v._id, x, y)))
        return v

    def step(self, tick, grid):
        """Step each vehicle in traffic list"""
        for insct in self.inscts.values():
            insct.step(tick, self.vehicles)

        for v in self.vehicles:
            entering_insct, segment_dir = v.step(tick, grid)
            if entering_insct:
                self._add_vehicle_to_insct(v, segment_dir)

    def _add_vehicle_to_insct(self, vehicle, drctn: Direction):
        r, c = world_coords_to_grid_index(
            self.config.TILE_WIDTH,
            self.config.TILE_HEIGHT,
            *vehicle._world_coords
        )

        if not self.inscts.get((r, c)):
            self.inscts[(r, c)] = Intersection(self.config)

        self.inscts[(r, c)].enqueue(vehicle, drctn)

    def get_updates(self) -> List[Tuple[Update, Tuple[int, float, float]]]:
        """Get updates and clear updates queue"""
        updates = self.updates

        # For now, always assume a Vehicle has moved
        for v in self.vehicles:
            x, y = v._world_coords
            updates.append((Update.MODIFIED, (v._id, x, y)))

        self.updates = []
        return updates


class Intersection:
    """An Intersection construct that determines how Vehicles pass between
    intersection edge nodes in the TravelGraph.

    Behaves as if all segment directions have a stop sign.
    """

    def __init__(self, config):
        self.config = config

        self.queues: Dict(Direction, int) = {
            Direction.UP: [],  # list of vehicle ids
            Direction.RIGHT: [],
            Direction.DOWN: [],
            Direction.LEFT: [],
        }
        self.wait_timers: Dict(Direction, float) = {
            Direction.UP: 0,
            Direction.RIGHT: 0,
            Direction.DOWN: 0,
            Direction.LEFT: 0,
        }

        self._last_dequeue_dir = Direction.LEFT  # so UP goes first

        # Timer to give vehicle in the middle of the intersection time to leave
        # the intersection before dequeuing the next vehicle in the
        # intersection.
        self._clear_timer = 0

    def enqueue(self, vehicle, drctn: Direction):
        """Add vehicle to direction queue"""
        if not self.queues[drctn]:
            self.wait_timers[drctn] = self.config.VEHICLE_STOP_WAIT_TIME
        self.queues[drctn].append(vehicle._id)
        vehicle._waiting_at_insct = True

    def _dequeue(self, drctn: Direction, vehicles):
        """Remove vehicle from direction queue"""
        vehicle_id = self.queues[drctn].pop(0)
        vehicles[vehicle_id]._waiting_at_insct = False

        if self.queues[drctn]:
            self.wait_timers[drctn] = self.config.VEHICLE_STOP_WAIT_TIME

    def step(self, tick, vehicles):
        """Release vehicles from their queues, when possible"""

        for direction, timer in self.wait_timers.items():
            self.wait_timers[direction] = max(timer - tick, 0)

        self._clear_timer = max(self._clear_timer - tick, 0)
        if self._clear_timer > 0:
            return

        # Vehicles should enter the intersection in a clockwise rotation.
        # Determine order of directions to let out by rotating our list.
        #     Example: DOWN let out last.
        #       [UP, RIGHT, DOWN, LEFT] -> [LEFT, UP, RIGHT, DOWN]
        #     Example: RIGHT let out last.
        #       [UP, RIGHT, DOWN, LEFT] -> [DOWN, LEFT, UP, RIGHT]
        dir_order = deque(
            [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        )
        dir_order.rotate(-1 * (self._last_dequeue_dir + 1))

        for drctn in dir_order:
            if self.wait_timers[drctn] > 0:
                continue

            if self.queues[drctn]:
                self._dequeue(drctn, vehicles)
                self._last_dequeue_dir = drctn
                self._clear_timer = self.config.INTERSECTION_CLEAR_TIME
                break


class Vehicle:
    """A Vehicle that travels along the TravelGraph"""

    def __init__(self, config, id, node: RoadSegmentNode):
        self.config = config

        # Attributes
        self._id = id
        self.speed = (
            1 * config.TILE_WIDTH
        )  # WARNING: could have undesirable behavior

        # Location
        self._world_coords = node.world_coords

        # Travel path
        self._path = []
        self._last_t_node = node  # last target node

        self._t_node = None  # target node
        self._trajectory = None

        # Intersection
        self._waiting_at_insct = False

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

        trajectory = pathing.LinearTrajectory(
            *self._world_coords, *self._t_node.world_coords
        )
        self._trajectory = trajectory

    def step(self, tick, grid) -> (bool, Direction):
        """Move a distance based on our speed towards the next node in our
        path, readjusting targets as needed in case we reach them mid-step.

        Notify if the vehicle is entering an intersection, to be queued.

        returns: (entering_insct, segment_dir)
        """
        remaining_move_dist = self.speed * tick

        while not self._waiting_at_insct and remaining_move_dist > 0:
            if not self._path:
                return False, None

            if not self._has_target():
                self._set_target()

            # Attempt move towards target
            dist_moved = self._move_towards_target(
                self._trajectory, remaining_move_dist
            )
            remaining_move_dist -= dist_moved

            entering_insct = self.entering_insct(grid)

            # Target reached
            if self._world_coords == self._t_node.world_coords:
                self._last_t_node = self._path.pop(0)

                if self._path:
                    self._set_target()
                else:
                    self._clear_target()

            # Target was an intersection
            if entering_insct:
                return True, self._last_t_node.dir

        return False, None

    def entering_insct(self, grid):
        """Returns True if Vehicle at the edge of an intersection, waiting to
        enter.
        """
        if (
            self._world_coords == self._t_node.world_coords
            and self._t_node.node_type == RoadNodeType.ENTER
        ):

            r, c = world_coords_to_grid_index(
                self.config.TILE_WIDTH,
                self.config.TILE_HEIGHT,
                *self._world_coords
            )
            return grid.tile_type(r, c).is_intersection()

        return False
