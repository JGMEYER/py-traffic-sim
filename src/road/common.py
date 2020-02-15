from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import List, Tuple

###################
# Tile properties #
###################


class TileType(IntEnum):
    """Tile patterns and their orientations"""

    # no tile
    EMPTY = 0
    # no neighbors
    ALONE = 1
    # one neighbor
    UP = 2
    RIGHT = 3
    DOWN = 4
    LEFT = 5
    # two neighbors
    UP_RIGHT = 6  # ╚
    RIGHT_DOWN = 7  # ╔
    DOWN_LEFT = 8  # ╗
    UP_LEFT = 9  # ╝
    UP_DOWN = 10  # ║
    RIGHT_LEFT = 11  # ═
    # three neighbors
    UP_RIGHT_DOWN = 12  # ╠
    RIGHT_DOWN_LEFT = 13  # ╦
    UP_DOWN_LEFT = 14  # ╣
    UP_RIGHT_LEFT = 15  # ╩
    # four neighbors
    UP_RIGHT_DOWN_LEFT = 16  # ╬

    def segment_directions(self):
        """Returns directions of road segments associated with tile type"""
        dirs = []
        if "UP" in self.name:
            dirs.append(Direction.UP)
        if "RIGHT" in self.name:
            dirs.append(Direction.RIGHT)
        if "DOWN" in self.name:
            dirs.append(Direction.DOWN)
        if "LEFT" in self.name:
            dirs.append(Direction.LEFT)
        return dirs

    def is_intersection(self):
        """Returns if True if TileType is an intersection"""
        return len(self.segment_directions()) >= 3


def grid_index_to_world_coords(tile_width, tile_height, r, c, center=False):
    """Convert (row, col) index on the grid to (x, y) coordinate on the world
    plane.
    """
    if center:
        return (
            c * tile_width + tile_width // 2,
            r * tile_height + tile_height // 2,
        )
    else:
        return (c * tile_width, r * tile_height)


def world_coords_to_grid_index(tile_width, tile_height, x: float, y: float):
    """Convert (x, y) coordinate on the world plane to the corresponding
    (row, col) index on the grid.
    """
    # Elsewhere in the code we may use numpy to perform arithmetic. Problem is,
    # numpy.float64 values don't cast well to int and will ignore floor
    # division, even when explicitly specified with "//". This is a hack
    # solution to get around this which hopefully shouldn't have negative
    # consequences with how this function is used. Time will tell.
    x, y = int(x), int(y)

    return (y // tile_height, x // tile_width)


####################
# Graph properties #
####################


class RoadNodeType(IntEnum):
    """Entry and exit nodes for road segments"""

    ENTER = 0
    EXIT = 1


###########
# General #
###########


class Direction(IntEnum):
    """Directions"""

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def opposite(self):
        """Returns direction opposite of this direction"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
        }
        return opposites[self]


class Update(IntEnum):
    """Update types"""

    ADDED = 0
    REMOVED = 1
    MODIFIED = 2


class Updateable(metaclass=ABCMeta):
    """A class that is has trackable updates."""

    @abstractmethod
    def get_updates() -> List[Tuple[Update, object]]:
        """Retrieve latest updates. Updates queue MUST be cleared once called.
        """
        raise NotImplementedError
