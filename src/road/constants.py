from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import List, Tuple

###################
# Tile properties #
###################

TILE_WIDTH = 64
TILE_HEIGHT = 64
ROAD_WIDTH = 30
# Constraints
assert TILE_WIDTH % 2 == 0
assert TILE_HEIGHT % 2 == 0
assert ROAD_WIDTH % 2 == 0


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
    UP_RIGHT = 6             # ╚
    RIGHT_DOWN = 7           # ╔
    DOWN_LEFT = 8            # ╗
    UP_LEFT = 9              # ╝
    UP_DOWN = 10             # ║
    RIGHT_LEFT = 11          # ═
    # three neighbors
    UP_RIGHT_DOWN = 12       # ╠
    RIGHT_DOWN_LEFT = 13     # ╦
    UP_DOWN_LEFT = 14        # ╣
    UP_RIGHT_LEFT = 15       # ╩
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


def grid_index_to_world_coords(r, c, center=False):
    """Convert (row, col) index on the grid to (x, y) coordinate on the world
    plane.
    """
    if center:
        return (c*TILE_WIDTH+TILE_WIDTH//2, r*TILE_HEIGHT+TILE_HEIGHT//2)
    else:
        return (c*TILE_WIDTH, r*TILE_HEIGHT)


def world_coords_to_grid_index(x, y):
    """Convert (x, y) coordinate on the world plane to the corresponding
    (row, col) index on the grid.
    """
    return (y//TILE_HEIGHT, x//TILE_WIDTH)


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



if __name__ == "__main__":
    print(TileType.UP_RIGHT_DOWN_LEFT.segment_directions())
