from dataclasses import dataclass
from typing import Dict, Tuple

import networkx as nx

from .constants import (
    TILE_WIDTH as tw,
    TILE_HEIGHT as th,
    Direction,
    RoadNodeType,
    TileType,
)


#############
# Tile Grid #
#############

class TileGrid():
    """A 2d grid of all road tiles"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[TileType.EMPTY for c in range(w)] for r in range(h)]

    def tile_type(self, r, c):
        """Return tile type of tile at index (r, c)"""
        return TileType(self.grid[r][c])

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
            return TileType.UP_RIGHT_DOWN_LEFT

    def get_neighbors(self, r, c):
        """Get tuple of bools for occupied tiles adjacent to tile coordinate"""
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


################
# Travel Graph #
################

@dataclass
class RoadSegmentNode:
    """An ENTER or EXIT travel node on a road segment.

    A road segment is any "active" road on a particular tile, e.g. an
    UP_DOWN_LEFT tile has an UP, DOWN, and LEFT segment."""
    pos: Tuple[int, int]
    dir: Direction
    node_type: RoadNodeType


class TravelIntersection():
    """An intersection on the TileGrid comprised of nodes on the TravelGraph
    that represents all ENTER and EXIT travel nodes for the given tile.

    Each road segment on a tile (i.e. UP, RIGHT, DOWN, LEFT) has an ENTER and
    EXIT node denoting where traffic flows into and out of the tile,
    respectively.

    Structure:
        self.nodes = {
            Direction {
                RoadNodeType.ENTER: RoadSegmentNode,
                RoadNodeType.EXIT: RoadSegmentNode,
            },
            ..
        }
    """

    def __init__(self, r, c, tile_type):
        self.nodes = {}
        for dir in tile_type.segment_directions():
            self.nodes[dir] = RoadSegmentNode((r, c), dir, RoadNodeType.ENTER)
            self.nodes[dir] = RoadSegmentNode((r, c), dir, RoadNodeType.EXIT)

    def enter_nodes(self):
        """Return all ENTER nodes in the intersection"""
        return [self.nodes[dir][RoadSegmentNode.ENTER]
                for dir in self.nodes.keys()]

    def exit_nodes(self):
        """Return all EXIT nodes in the intersection"""
        return [self.nodes[dir][RoadSegmentNode.EXIT]
                for dir in self.nodes.keys()]


# TODO update class docstring
# TODO add docstrings
class TravelGraph():
    """A graph of all intersection nodes

    Note: the current implementation treats every road tile as a node in the
    graph and thus is very unoptimized. Future iterations should only include
    road intersections as nodes in the graph.
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self.intersections: Dict[Tuple[int, int], TravelIntersection] = {}

    def register_tile_intersection(self, r, c, tile_type,
                                   nbrs: Dict[Direction, Tuple[Tuple[int, int],
                                                               TileType]]):
        intrsct = Intersection(r, c, tile_type)

        # TODO connect all nodes in segments as appropriate (stright, right, left turns)
        # TODO recreate all neighbor intersections (nodes) and add edges to all
        #      their neighbors. this should effectively add the center node
        #      to the grid

        self.intersections[(r, c)] = intersct

    def _connect_nodes_in_intersection():
        # TODO rename
        # TODO connect all nodes in segments as appropriate (stright, right, left turns)
        pass

    def shortest_path(self, r_a, c_a, r_b, c_b):
        pass

    # def add_node(self, pos, n_pos: List[Tuple[int, int]]):
    #     """Add node to the graph
    #
    #     r - road tile row
    #     c - road tile column
    #     n_pos - neighbor positions of provided road tile position
    #     """
    #     self.G.add_node(pos)
    #     for n in n_pos:
    #         # Add two-way edge
    #         self.G.add_edge(pos, n, length=1)

    # def shortest_path(self, source_pos, target_pos):
    #     """Get the shortest path from source tile to target tile"""
    #     return nx.shortest_path(self.G, source=source_pos, target=target_pos)
