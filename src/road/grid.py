from dataclasses import dataclass, field, InitVar
from typing import Dict, List, Tuple

import networkx as nx

from .common import (
    Direction,
    RoadNodeType,
    TileType,
    Update,
    Updateable,
    grid_index_to_world_coords,
)


#############
# Tile Grid #
#############


class TileGrid(Updateable):
    """A 2d grid of all road tiles"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[TileType.EMPTY for c in range(w)] for r in range(h)]
        self.updates = []

    def tile_type(self, r, c):
        """Return tile type of tile at index (r, c)"""
        return TileType(self.grid[r][c])

    def add_tile(self, r, c, restrict_to_neighbors=True):
        """Add tile to grid

        restrict_to_neighbors - only allow road to be placed next to an
                                existing tile
        returns: tile placed
        """
        if self.grid[r][c] != TileType.EMPTY:
            return False
        if restrict_to_neighbors and not self.get_neighbors(r, c).keys():
            return False

        self.update_tile_type(r, c, added=True)

        # Update tile types of adjacent tiles
        if r - 1 >= 0:
            self.update_tile_type(r - 1, c)
        if c + 1 < self.w:
            self.update_tile_type(r, c + 1)
        if r + 1 < self.h:
            self.update_tile_type(r + 1, c)
        if c - 1 >= 0:
            self.update_tile_type(r, c - 1)

        return True

    def update_tile_type(self, r, c, added=False):
        """Update the tile type for the tile at the provided coordinate.

        added - whether the tile is being added to the grid, i.e. changed from
                TileType.EMPTY via this operation
        """
        old_type = self.grid[r][c]
        new_type = self.evaluate_tile_type(r, c, added=added)

        if new_type != old_type:
            self.grid[r][c] = new_type
            u_type = Update.ADDED if added else Update.STATE_CHANGED
            self.updates.append((u_type, (r, c, new_type)))

    def evaluate_tile_type(self, r, c, added=False):
        """Determine the tile type for the tile at the provided coordinate.

        added - whether the tile would be newly added to the grid, i.e. changed
                from TileType.EMPTY
        """
        # Don't update empty spaces unless we recently added a tile there
        if not added and self.grid[r][c] == TileType.EMPTY:
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
        """Get tile metadata of neighbors adjacent to specified tile index"""
        nbrs: Dict[Direction, Tuple[Tuple[int, int], TileType]] = {}

        if r - 1 >= 0 and self.tile_type(r - 1, c) != TileType.EMPTY:
            nbrs[Direction.UP] = ((r - 1, c), self.tile_type(r - 1, c))

        if c + 1 < self.w and self.tile_type(r, c + 1) != TileType.EMPTY:
            nbrs[Direction.RIGHT] = ((r, c + 1), self.tile_type(r, c + 1))

        if r + 1 < self.h and self.tile_type(r + 1, c) != TileType.EMPTY:
            nbrs[Direction.DOWN] = ((r + 1, c), self.tile_type(r + 1, c))

        if c - 1 >= 0 and self.tile_type(r, c - 1) != TileType.EMPTY:
            nbrs[Direction.LEFT] = ((r, c - 1), self.tile_type(r, c - 1))

        return nbrs

    def get_updates(self) -> List[Tuple[Update, Tuple[int, int, TileType]]]:
        """Get updates and clear updates queue"""
        updates = self.updates
        self.updates = []
        return updates


################
# Travel Graph #
################


@dataclass(eq=True, frozen=True)  # make hashable
class RoadSegmentNode:
    """An ENTER or EXIT travel node on a road segment.

    A road "segment" is any active road on a particular tile, e.g. an
    UP_DOWN_LEFT tile has an UP, DOWN, and LEFT segment.
    """

    tile_index: Tuple[int, int]  # (r, c)
    dir: Direction
    node_type: RoadNodeType
    world_coords: Tuple[int, int] = field(init=False)

    config: InitVar[object]

    def __post_init__(self, config):
        """Get location of `RoadSegmentNode` on the world plane."""
        r, c = self.tile_index
        x, y = grid_index_to_world_coords(
            config.TILE_WIDTH, config.TILE_HEIGHT, r, c, center=True
        )

        if self.dir == Direction.UP:
            y -= config.TILE_HEIGHT // 4
            if self.node_type == RoadNodeType.ENTER:
                x -= config.ROAD_WIDTH // 2 // 2
            elif self.node_type == RoadNodeType.EXIT:
                x += config.ROAD_WIDTH // 2 // 2

        elif self.dir == Direction.RIGHT:
            x += config.TILE_WIDTH // 4
            if self.node_type == RoadNodeType.ENTER:
                y -= config.ROAD_WIDTH // 2 // 2
            elif self.node_type == RoadNodeType.EXIT:
                y += config.ROAD_WIDTH // 2 // 2

        elif self.dir == Direction.DOWN:
            y += config.TILE_HEIGHT // 4
            if self.node_type == RoadNodeType.ENTER:
                x += config.ROAD_WIDTH // 2 // 2
            elif self.node_type == RoadNodeType.EXIT:
                x -= config.ROAD_WIDTH // 2 // 2

        elif self.dir == Direction.LEFT:
            x -= config.TILE_WIDTH // 4
            if self.node_type == RoadNodeType.ENTER:
                y += config.ROAD_WIDTH // 2 // 2
            elif self.node_type == RoadNodeType.EXIT:
                y -= config.ROAD_WIDTH // 2 // 2

        # Hack to get around frozen=True. We don't care that we're mutating
        # an "immutable" object on __init__().
        object.__setattr__(self, "world_coords", (x, y))


class TravelIntersection:
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

    def __init__(self, config, r, c, tile_type):
        self.config = config
        self.r = r
        self.c = c
        self.nodes = {}
        for dir in tile_type.segment_directions():
            self.add_segment_nodes(dir)

    def segments(self):
        """Return road segments associated with tile"""
        return self.nodes.keys()

    def add_segment_nodes(self, dir: Direction):
        """Add all ENTER and EXIT nodes for a specified tile road segment"""
        self.nodes[dir] = {
            RoadNodeType.ENTER: RoadSegmentNode(
                (self.r, self.c), dir, RoadNodeType.ENTER, config=self.config,
            ),
            RoadNodeType.EXIT: RoadSegmentNode(
                (self.r, self.c), dir, RoadNodeType.EXIT, config=self.config,
            ),
        }

    def enter_nodes(self):
        """Return all ENTER nodes in the intersection"""
        return [
            self.nodes[dir][RoadNodeType.ENTER] for dir in self.nodes.keys()
        ]

    def exit_nodes(self):
        """Return all EXIT nodes in the intersection"""
        return [
            self.nodes[dir][RoadNodeType.EXIT] for dir in self.nodes.keys()
        ]

    def get_nodes_for_segment(self, dir):
        """Return (ENTER, EXIT) nodes tuple for segment"""
        return (
            self.nodes[dir][RoadNodeType.ENTER],
            self.nodes[dir][RoadNodeType.EXIT],
        )


class TravelGraph(Updateable):
    """A graph of all intersection nodes

    All nodes are of type `RoadSegmentNode`.

    Note: the current implementation adds nodes to every road tile in the graph
    and thus is unoptimized. Future iterations could only include nodes in road
    intersections, i.e. no straightaways, like UP_DOWN and RIGHT_LEFT tiles.
    """

    def __init__(self, config):
        self.config = config
        self.G = nx.DiGraph()
        self.intersections: Dict[Tuple[int, int], TravelIntersection] = {}
        self.updates = []

    def _add_edge(self, u_node, v_node):
        """Add edge. This should be called instead of adding to the graph
        directly."""
        # Only post update if change made
        if not self.G.has_edge(u_node, v_node):
            self.updates.append((Update.ADDED, (u_node, v_node)))
            self.G.add_edge(u_node, v_node)

    def _remove_edge(self, u_node, v_node):
        """Remove edge. This should be called instead of removing from the
        graph directly."""
        # Only post update if change made
        if self.G.has_edge(u_node, v_node):
            self.updates.append((Update.REMOVED, (u_node, v_node)))
            self.G.remove_edge(u_node, v_node)

    def register_tile_intersection(
        self,
        r,
        c,
        tile_type,
        nbrs: Dict[Direction, Tuple[Tuple[int, int], TileType]],
    ):
        """Add new intersection to TravelGraph"""
        # Create and intraconnect nodes for new intersection
        insct = TravelIntersection(self.config, r, c, tile_type)
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
            self._update_intersection_intraconnected_edges(n_insct)

        # Add edges between intersection and neighbor intersections
        for dir, ((n_r, n_c), tile_type) in nbrs.items():
            n_insct = self.intersections[(n_r, n_c)]
            enter, exit = insct.get_nodes_for_segment(dir)
            n_enter, n_exit = n_insct.get_nodes_for_segment(dir.opposite())
            self._add_edge(exit, n_enter)
            self._add_edge(n_exit, enter)

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
                self._remove_edge(enter, exit)
            except nx.NetworkXError:
                # No edge between enter and exit
                pass

        self._intraconnect_nodes(insct)

    def _intraconnect_nodes(self, insct):
        """Connect all ENTER and EXIT nodes within segments in an
        intersection.
        """
        segments = list(insct.segments())

        # Only one segment. Connect the two nodes, so vehicles can make a
        # U-Turn at dead-ends.
        if len(segments) == 1:
            enter, exit = insct.get_nodes_for_segment(segments[0])
            self._add_edge(enter, exit)

        # Connect segments' ENTER nodes to other segments' EXIT nodes
        # This is overkill when we're updating an intersection since most edges
        # already exist, but since this likely only happens on a player action
        # and not in the game loop we're ok with the efficiency hit.
        else:
            for enter in insct.enter_nodes():
                for exit in insct.exit_nodes():
                    # Don't connect any segments to themselves
                    if exit.dir == enter.dir:
                        continue
                    # Add the edge, even if it already exists
                    self._add_edge(enter, exit)

    def shortest_path(self, source_node, target_node):
        """Get the shortest path from source node to target node"""
        return nx.shortest_path(self.G, source=source_node, target=target_node)

    def get_updates(
        self,
    ) -> List[Tuple[Update, Tuple[RoadSegmentNode, RoadSegmentNode]]]:
        """Get updates and clear updates queue"""
        updates = self.updates
        self.updates = []
        return updates
