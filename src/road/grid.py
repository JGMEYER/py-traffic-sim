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

        nbrs = self.get_neighbors(r, c)

        count = len(nbrs.keys())
        up = nbrs.get(Direction.UP)
        right = nbrs.get(Direction.RIGHT)
        down = nbrs.get(Direction.DOWN)
        left = nbrs.get(Direction.LEFT)

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
        """Get tile neighbors adjacent to specified tile index """
        nbrs: Dict[Direction, Tuple[Tuple[int, int], TileType]] = {}

        if r-1 >= 0 and self.tile_type(r-1, c) != TileType.EMPTY:
            nbrs[Direction.UP] = ((r-1, c), self.tile_type(r-1, c))

        if c+1 < self.w and self.tile_type(r, c+1) != TileType.EMPTY:
            nbrs[Direction.RIGHT] = ((r, c+1), self.tile_type(r, c+1))

        if r+1 < self.h and self.tile_type(r+1, c) != TileType.EMPTY:
            nbrs[Direction.DOWN] = ((r+1, c), self.tile_type(r+1, c))

        if c-1 >= 0 and self.tile_type(r, c-1) != TileType.EMPTY:
            nbrs[Direction.LEFT] = ((r, c-1), self.tile_type(r, c-1))

        return nbrs


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
        self.r = r
        self.c = c
        self.nodes = {}
        for dir in tile_type.segment_directions():
            self.add_segment_nodes()

    def segments(self):
        """Return road segments associated with tile"""
        return self.node.keys()

    def add_segment_nodes(self, dir: Direction):
        """Add all ENTER and EXIT nodes for a specified tile road segment"""
        self.nodes[dir] = RoadSegmentNode((self.r, self.c), dir,
                                          RoadNodeType.ENTER)
        self.nodes[dir] = RoadSegmentNode((self.r, self.c), dir,
                                          RoadNodeType.EXIT)

    def enter_nodes(self):
        """Return all ENTER nodes in the intersection"""
        return [self.nodes[dir][RoadSegmentNode.ENTER]
                for dir in self.nodes.keys()]

    def exit_nodes(self):
        """Return all EXIT nodes in the intersection"""
        return [self.nodes[dir][RoadSegmentNode.EXIT]
                for dir in self.nodes.keys()]

    def get_nodes_for_segment(self, dir):
        """Return (ENTER, EXIT) nodes tuple for segment"""
        return (self.nodes[dir][RoadNodeType.ENTER],
                self.nodes[dir][RoadNodeType.EXIT])


# TODO add docstrings
class TravelGraph():
    """A graph of all intersection nodes

    Note: the current implementation adds nodes to every road tile in the graph
    and thus is very unoptimized. Future iterations should only include road
    intersections, i.e. no straightaways, like UP_DOWN and RIGHT_LEFT tiles.
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self.intersections: Dict[Tuple[int, int], TravelIntersection] = {}

    def register_tile_intersection(self, grid, r, c, tile_type,
                                   nbrs: Dict[Direction, Tuple[Tuple[int, int],
                                                               TileType]]):
        """Add new intersection to TravelGraph"""
        # Create and intraconnect nodes for new intersection
        insct = TravelIntersection(r, c, tile_type)
        self._intraconnect_nodes(insct)

        # Neighbor intersections will have a new segment added to their tile to
        # bridge the connection to the newly placed tile. Add ENTER and EXIT
        # nodes to all neighbor's new segments and recompute their
        # intraconnected edges to account for this update.
        for dir, ((n_r, n_c), tile_type) in nbrs.items():
            n_insct = self.intersections[(n_r, n_c)]
            # Add nodes to new segment
            n_insct.add_segment_nodes(dir.opposite())
            # Update edges
            self._update_intersection_intraconnected_edges(n_r, n_c)

        # Add edges between intersection and neighbor intersections
        for dir, ((n_r, n_c), tile_type) in nbrs.items():
            n_insct = self.intersections[(n_r, n_c)]
            enter, exit = insct.get_nodes_for_segment(dir)
            n_enter, n_exit = n_insct.get_nodes_for_segment(dir.opposite())
            self.G.add_edge((exit, n_enter))
            self.G.add_edge((n_exit, enter))

        self.intersections[(r, c)] = insct

    def _update_intersection_intraconnected_edges(self, insct):
        """Update existing intersection's edges to match desired configuration
        for current set of nodes.

        Should only be used on existing intersections in the graph that have
        been updated via a road adjacent to it, i.e. do not run this for newly
        placed dead-end tiles.
        """
        # Clear all self-connected edges from existing dead-end segments
        # We don't know which one was newly added, so go through each segment
        # and try removing any self-connections.
        for dir in insct.segments():
            enter, exit = insct.get_nodes_for_segment(dir)
            try:
                self.G.remove_edge((enter, exit))
            except nx.NetworkXError:
                # No edge between enter and exit
                pass

        self._intraconnect_nodes(insct)

    def _intraconnect_nodes(self, insct):
        """Connect all ENTER and EXIT nodes within segments in an
        intersection.
        """
        # Only one segment. Connect the two nodes, so vehicles can make a
        # U-Turn at dead-ends.
        if len(insct.segments()) == 1:
            enter_node, exit_node = \
                insct.get_nodes_for_segment(insct.segments()[0])
            self.G.add_edge(enter_node, exit_node)

        # Connect segments' ENTER nodes to other segments' EXIT nodes
        # This is overkill when we're updating an intersection since most edges
        # already exist, but since this likely only happens on a player action
        # and not in the game loop we're ok with the efficiency hit.
        else:
            for enter_node in insct.enter_nodes():
                for exit_node in insct.exit_nodes():
                    # Don't connect any segments to themselves
                    if exit_node.dir == enter_node.dir:
                        continue
                    # Add the edge, even if it already exists
                    self.G.add_edge(enter_node, exit_node)

    def shortest_path(self, r_a, c_a, r_b, c_b):
        """Get the shortest path from source tile to target tile"""
        # TODO implement -- could be tricky since a Vehicle will no longer map
        # to just a singular node on a tile, we need to figure out which lane
        # they're in
        # nx.shortest_path(self.G, source=source_node, target=target_node)
        pass
