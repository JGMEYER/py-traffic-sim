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
    UP_RIGHT = 6          # ╚
    RIGHT_DOWN = 7        # ╔
    DOWN_LEFT = 8         # ╗
    UP_LEFT = 9           # ╝
    UP_DOWN = 10          # ║
    RIGHT_LEFT = 11       # ═
    # three neighbors
    UP_RIGHT_DOWN = 12    # ╠
    RIGHT_DOWN_LEFT = 13  # ╦
    UP_DOWN_LEFT = 14     # ╣
    UP_RIGHT_LEFT = 15    # ╩
    # four neighbors
    ALL = 16              # ╬
