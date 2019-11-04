import pygame

from . import grid

# A lot of assumptions are made using these -- for now, do not modify
TILE_WIDTH = 30
TILE_HEIGHT = 30

TILE_POLYGONS = {
    # no tile
    grid.TILE_EMPTY: [],
    # no neighbors
    grid.TILE_ALONE: [(10, 10), (20, 10), (20, 20), (10, 20)],
    # one neighbor
    grid.TILE_UP: [(10, 0), (20, 0), (20, 20), (10, 20)],
    grid.TILE_RIGHT: [(10, 10), (30, 10), (30, 20), (10, 20)],
    grid.TILE_DOWN: [(10, 10), (20, 10), (20, 30), (10, 30)],
    grid.TILE_LEFT: [(0, 10), (20, 10), (20, 20), (0, 20)],
    # two neighbors
    grid.TILE_UP_RIGHT: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (10, 20), (10, 0)],
    grid.TILE_RIGHT_DOWN: [(10, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 10)],
    grid.TILE_DOWN_LEFT: [(0, 10), (20, 10), (20, 30), (10, 30), (10, 20), (0, 20)],
    grid.TILE_UP_LEFT: [(10, 0), (20, 0), (20, 20), (0, 20), (0, 10), (10, 10)],
    grid.TILE_UP_DOWN: [(10, 0), (20, 0), (20, 30), (10, 30)],
    grid.TILE_RIGHT_LEFT: [(0, 10), (30, 10), (30, 20), (0, 20)],
    # three neighbors
    grid.TILE_UP_RIGHT_DOWN: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30)],
    grid.TILE_RIGHT_DOWN_LEFT: [(0, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 20), (0, 20)],
    grid.TILE_UP_DOWN_LEFT: [(10, 0), (20, 0), (20, 30), (10, 30), (10, 20), (0, 20), (0, 10), (10, 10)],
    grid.TILE_UP_RIGHT_LEFT: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (0, 20), (0, 10), (10, 10)],
    # four neighbors
    grid.TILE_ALL: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 20), (0, 20), (0, 10), (10, 10)],
}


def render_tile(window, r, c, road_type):
    """Draw single road tile to window"""
    points = TILE_POLYGONS[road_type]
    if not points:
        return
    translated_points = [(x + TILE_WIDTH * c, y + TILE_HEIGHT * r)
                         for (x, y) in points]
    pygame.draw.polygon(window, (0, 0, 0), translated_points)


def render_grid(window, grid):
    """Draw all road tiles in grid to window"""
    for r in range(grid.h):
        for c in range(grid.w):
            render_tile(window, r, c, grid.grid[r][c])
