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
            nbrs = self.get_neighbors(self.grid, r, c)
            self.graph.register_tile_intersection(r, c,
                                                  self.grid.tile_type(r, c),
                                                  nbrs)
            return True
        return False

    # TODO rm?
    # def get_neighborhood(self, r, c):
    #     """
    #     Returns a dict of neighbors (primary) for the given tile index and all
    #     of their neighbors' neighbors (secondary).
    #
    #     Spread, visualized:
    #
    #         ┌───┬───┬───┬───┬───┐
    #         │   │   │ * │   │   │
    #         ├───┼───┼───┼───┼───┤
    #         │   │ * │ n1│ * │   │
    #         ├───┼───┼───┼───┼───┤
    #         │ * │ n4│ o │ n2│ * │
    #         ├───┼───┼───┼───┼───┤
    #         │   │ * │ n3│ * │   │
    #         ├───┼───┼───┼───┼───┤
    #         │   │   │ * │   │   │
    #         └───┴───┴───┴───┴───┘
    #
    #         o = origin index
    #         n = primary neighbor
    #         * = secondary neighbor
    #
    #     The final dictionary keys on all 'o' and 'n' tile indexes and contains
    #     all neighbors adjacent to each of the key tile indexes.
    #
    #     Returns:
    #         nbrhood = {
    #             (r_o, c_o): {
    #                 Direction.UP: ((r1, c1), TileType),
    #                 Direction.DOWN: ((r2, c2), TileType),
    #                 Direction.LEFT: ((r3, c3), TileType),
    #                 Direction.RIGHT: ((r4, c4), TileType),
    #             },
    #             (r_n1, r_n1): { .. },
    #             (r_n2, r_n2): { .. },
    #             (r_n3, r_n3): { .. },
    #             (r_n4, r_n4): { .. },
    #         }
    #     """
    #     nbrhood = {}
    #     nbrs = self.grid.get_neighbors(r, c)
    #
    #     for n in nbrs:

    def step(self):
        """Step the network one tick"""
        self.traffic.step()
