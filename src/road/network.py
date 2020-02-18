from .grid import TileGrid, TravelGraph
from .traffic import Traffic


class RoadNetwork:
    """Controls all data structures necessary for storing and maintaining a
    road network.
    """

    def __init__(self, config, w, h):
        self.config = config

        self.w = w
        self.h = h

        # Network components
        self.grid = TileGrid(w, h)
        self.graph = TravelGraph(config)
        self.traffic = Traffic(config)

    def add_road(self, r, c, restrict_to_neighbors=True):
        """Add road node to the network

        returns: road added (bool)
        """
        tile_added = self.grid.add_tile(r, c, restrict_to_neighbors)
        if tile_added:
            nbrs = self.grid.get_neighbors(r, c)
            self.graph.register_tile_intersection(
                r, c, self.grid.tile_type(r, c), nbrs
            )
            return True
        return False

    def step(self, tick):
        """Step the network by some amount of ticks"""
        self.traffic.step(tick, self.grid)
