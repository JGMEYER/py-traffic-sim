from typing import Dict, Tuple

from .constants import Direction, TileType
from .grid import TileGrid, TravelGraph
from .traffic import Traffic


class RoadNetwork():
    """Controls all data structures necessary for storing and maintaining a
    road network.
    """

    def __init__(self, w, h):
        self.w = w
        self.h = h

        # Network components
        self.grid = TileGrid(w, h)
        self.graph = TravelGraph()
        self.traffic = Traffic()

        # Create starting road from which all other roads will connect
        self.seed_pos = (h//2, w//2)
        self.add_road(self.seed_pos, restrict_to_neighbors=False)

    def add_road(self, pos, restrict_to_neighbors=True):
        """Add road node to the network

        returns: road added (bool)"""
        r, c = pos
        tile_added = self.grid.add_tile(r, c, restrict_to_neighbors)
        if tile_added:
            nbrs = self.get_neighbor_positions(self.grid, r, c)
            self.graph.register_tile_intersection(r, c,
                                                  self.grid.tile_type(r, c),
                                                  nbrs)
            return True
        return False

    def get_neighbors(self, grid, r, c):
        """Get tile neighbors adjacent to specified tile index """
        nbrs: Dict[Direction, Tuple[Tuple[int, int], TileType]] = {}

        if r-1 >= 0 and grid.tile_type(r-1, c) != TileType.EMPTY:
            nbrs[Direction.UP] = ((r-1, c), grid.tile_type(r-1, c))

        if c+1 < self.w and grid.tile_type(r, c+1) != TileType.EMPTY:
            nbrs[Direction.RIGHT] = ((r, c+1), grid.tile_type(r, c+1))

        if r+1 < self.h and grid.tile_type(r+1, c) != TileType.EMPTY:
            nbrs[Direction.DOWN] = ((r+1, c), grid.tile_type(r+1, c))

        if c-1 >= 0 and grid.tile_type(r, c-1) != TileType.EMPTY:
            nbrs[Direction.LEFT] = ((r, c-1), grid.tile_type(r, c-1))

        return nbrs

    def step(self):
        """Step the network one tick"""
        self.traffic.step()
