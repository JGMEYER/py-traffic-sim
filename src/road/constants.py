from enum import IntEnum

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


if __name__ == "__main__":
    print(TileType.UP_RIGHT_DOWN_LEFT.segment_directions())
