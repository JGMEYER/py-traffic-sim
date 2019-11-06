from typing import List, Tuple

import networkx as nx

from .constants import (
    TILE_WIDTH as tw,
    TILE_HEIGHT as th,
    TileType,
)


class TileGrid():
    """A 2d grid of all road tiles"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[TileType.EMPTY for c in range(w)] for r in range(h)]

    def add_tile(self, r, c, restrict_to_neighbors=True):
        """Add tile to grid

        restrict_to_neighbors - only allow road to be placed next to an
                                existing tile
        """
        if self.grid[r][c] != TileType.EMPTY:
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
        if not modified and self.grid[r][c] == TileType.EMPTY:
            return TileType.EMPTY

        neighbors = self.get_neighbors(r, c)
        count = len([n for n in neighbors if n])
        up, right, down, left = neighbors

        if count == 0:
            return TileType.ALONE
        elif count == 1:
            if up:
                return TileType.UP
            elif right:
                return TileType.RIGHT
            elif down:
                return TileType.DOWN
            elif left:
                return TileType.LEFT
        elif count == 2:
            if up and right:
                return TileType.UP_RIGHT
            elif right and down:
                return TileType.RIGHT_DOWN
            elif down and left:
                return TileType.DOWN_LEFT
            elif up and left:
                return TileType.UP_LEFT
            elif up and down:
                return TileType.UP_DOWN
            elif right and left:
                return TileType.RIGHT_LEFT
        elif count == 3:
            if up and right and down:
                return TileType.UP_RIGHT_DOWN
            elif right and down and left:
                return TileType.RIGHT_DOWN_LEFT
            elif up and down and left:
                return TileType.UP_DOWN_LEFT
            elif up and right and left:
                return TileType.UP_RIGHT_LEFT
        elif count == 4:
            return TileType.ALL

    def get_neighbors(self, r, c):
        """Get tuple of occupied tiles adjacent to tile coordinate"""
        up = (r-1 >= 0 and self.grid[r-1][c] != TileType.EMPTY)
        right = (c+1 < self.w and self.grid[r][c+1] != TileType.EMPTY)
        down = (r+1 < self.h and self.grid[r+1][c] != TileType.EMPTY)
        left = (c-1 >= 0 and self.grid[r][c-1] != TileType.EMPTY)
        return (up, right, down, left)


def grid_index_to_world_coords(r, c, center=False):
    """Convert (row, col) index on the grid to (x, y) coordinate on the world
    plane.
    """
    if center:
        return (c*tw+tw//2, r*th+th//2)
    else:
        return (c*tw, r*th)


def world_coords_to_grid_index(x, y):
    """Convert (x, y) coordinate on the world plane to the corresponding
    (row, col) index on the grid.
    """
    return (y//th, x//tw)


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
