import random
from typing import List, Tuple

import networkx as nx


class RoadNetwork():
    """Controls all data structures necessary for storing and maintaining a
    road network.
    """

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = TileGrid(w, h)
        self.graph = TravelGraph()

        # Create starting road from which all other roads will connect
        self.seed_pos = (h//2, w//2)
        self.add_road(self.seed_pos, restrict_to_neighbors=False)

    def add_road(self, pos, restrict_to_neighbors=True):
        """Add road node to the network"""
        r, c = pos
        tile_added = self.grid.add_tile(r, c, restrict_to_neighbors)
        if tile_added:
            n_pos = self.get_neighbor_positions(self.grid.grid, r, c)
            self.graph.add_node((r, c), n_pos)
            return True
        return False

    def get_neighbor_positions(self, grid, r, c):
        """Get coordinates of adjacent tiles"""
        n_pos = []
        if r-1 >= 0 and grid[r-1][c] != TILE_EMPTY:
            n_pos.append((r-1, c))
        if c+1 < self.w and grid[r][c+1] != TILE_EMPTY:
            n_pos.append((r, c+1))
        if r+1 < self.h and grid[r+1][c] != TILE_EMPTY:
            n_pos.append((r+1, c))
        if c-1 >= 0 and grid[r][c-1] != TILE_EMPTY:
            n_pos.append((r, c-1))
        return n_pos


# no tile
TILE_EMPTY = 0
# no neighbors
TILE_ALONE = 1
# one neighbor
TILE_UP = 2
TILE_RIGHT = 3
TILE_DOWN = 4
TILE_LEFT = 5
# two neighbors
TILE_UP_RIGHT = 6          # ╚
TILE_RIGHT_DOWN = 7        # ╔
TILE_DOWN_LEFT = 8         # ╗
TILE_UP_LEFT = 9           # ╝
TILE_UP_DOWN = 10          # ║
TILE_RIGHT_LEFT = 11       # ═
# three neighbors
TILE_UP_RIGHT_DOWN = 12    # ╠
TILE_RIGHT_DOWN_LEFT = 13  # ╦
TILE_UP_DOWN_LEFT = 14     # ╣
TILE_UP_RIGHT_LEFT = 15    # ╩
# four neighbors
TILE_ALL = 16              # ╬


class TileGrid():
    """A 2d grid of all road tiles"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[TILE_EMPTY for c in range(w)] for r in range(h)]

    def add_tile(self, r, c, restrict_to_neighbors=True):
        """Add tile to grid

        restrict_to_neighbors - only allow road to be placed next to an
                                existing tile
        """
        if self.grid[r][c] != TILE_EMPTY:
            return False
        if restrict_to_neighbors and not any(self.get_neighbors(r, c)):
            return False

        self.grid[r][c] = self.evaluate_tile_type(r, c, modified=True)

        # re-evaluate tile types of adjacent grids
        if r-1 >= 0:
            self.grid[r-1][c] = self.evaluate_tile_type(r-1, c)
        if c+1 < self.w:
            self.grid[r][c+1] = self.evaluate_tile_type(r, c+1)
        if r+1 < self.h:
            self.grid[r+1][c] = self.evaluate_tile_type(r+1, c)
        if c-1 >= 0:
            self.grid[r][c-1] = self.evaluate_tile_type(r, c-1)

        return True

    def evaluate_tile_type(self, r, c, modified=False):
        """Determine the tile type for the tile at the provided coordinate.

        modified - whether the state of the tile was recently directly changed,
                   e.g. via an "add" or "remove" action
        """
        if not modified and self.grid[r][c] == TILE_EMPTY:
            return TILE_EMPTY

        neighbors = self.get_neighbors(r, c)
        count = len([n for n in neighbors if n])
        up, right, down, left = neighbors

        if count == 0:
            return TILE_ALONE
        elif count == 1:
            if up:
                return TILE_UP
            elif right:
                return TILE_RIGHT
            elif down:
                return TILE_DOWN
            elif left:
                return TILE_LEFT
        elif count == 2:
            if up and right:
                return TILE_UP_RIGHT
            elif right and down:
                return TILE_RIGHT_DOWN
            elif down and left:
                return TILE_DOWN_LEFT
            elif up and left:
                return TILE_UP_LEFT
            elif up and down:
                return TILE_UP_DOWN
            elif right and left:
                return TILE_RIGHT_LEFT
        elif count == 3:
            if up and right and down:
                return TILE_UP_RIGHT_DOWN
            elif right and down and left:
                return TILE_RIGHT_DOWN_LEFT
            elif up and down and left:
                return TILE_UP_DOWN_LEFT
            elif up and right and left:
                return TILE_UP_RIGHT_LEFT
        elif count == 4:
            return TILE_ALL

    def get_neighbors(self, r, c):
        """Get tuple of occupied tiles adjacent to tile coordinate"""
        up = (r-1 >= 0 and self.grid[r-1][c] != TILE_EMPTY)
        right = (c+1 < self.w and self.grid[r][c+1] != TILE_EMPTY)
        down = (r+1 < self.h and self.grid[r+1][c] != TILE_EMPTY)
        left = (c-1 >= 0 and self.grid[r][c-1] != TILE_EMPTY)
        return (up, right, down, left)


def random_grid(w, h):
    grid = TileGrid(w, h)
    for r in range(h):
        for c in range(w):
            if random.random() < 0.5:
                grid.add_tile(r, c)
    return grid


class TravelGraph():
    """A graph of all intersection nodes

    Note: the current implementation treats every road tile as a node in the
    graph and thus is very unoptimized. Future iterations should only include
    road intersections as nodes in the graph.
    """

    def __init__(self):
        self.G = nx.Graph()

    def add_node(self, pos, n_pos: List[Tuple[int, int]]):
        """Add node to the graph

        r - road tile row
        c - road tile column
        n_pos - neighbor positions of provided road tile position
        """
        self.G.add_node(pos)
        for n in n_pos:
            # Add two-way edge
            self.G.add_edge(pos, n, length=1)

    def shortest_path(self, source_pos, target_pos):
        """Get the shortest path from source tile to target tile"""
        return nx.shortest_path(self.G, source=source_pos, target=target_pos)


if __name__ == "__main__":
    """Tests"""
    grid = random_grid()
    print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                             for row in grid.grid]))