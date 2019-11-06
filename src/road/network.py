from .constants import TileType
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
        if r-1 >= 0 and grid[r-1][c] != TileType.EMPTY:
            n_pos.append((r-1, c))
        if c+1 < self.w and grid[r][c+1] != TileType.EMPTY:
            n_pos.append((r, c+1))
        if r+1 < self.h and grid[r+1][c] != TileType.EMPTY:
            n_pos.append((r+1, c))
        if c-1 >= 0 and grid[r][c-1] != TileType.EMPTY:
            n_pos.append((r, c-1))
        return n_pos

    def step(self):
        """Step the network one tick"""
        self.traffic.step()
