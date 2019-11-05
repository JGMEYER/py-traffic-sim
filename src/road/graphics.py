from typing import Tuple

import pygame

from .constants import TileType

# WARNING: for now, do not modify - tile polygons will not scale to dimensions
TILE_WIDTH = 30
TILE_HEIGHT = 30

TILE_POLYGONS = {
    # no tile
    TileType.EMPTY: [],
    # no neighbors
    TileType.ALONE: [(10, 10), (20, 10), (20, 20), (10, 20)],
    # one neighbor
    TileType.UP: [(10, 0), (20, 0), (20, 20), (10, 20)],
    TileType.RIGHT: [(10, 10), (30, 10), (30, 20), (10, 20)],
    TileType.DOWN: [(10, 10), (20, 10), (20, 30), (10, 30)],
    TileType.LEFT: [(0, 10), (20, 10), (20, 20), (0, 20)],
    # two neighbors
    TileType.UP_RIGHT: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (10, 20), (10, 0)],
    TileType.RIGHT_DOWN: [(10, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 10)],
    TileType.DOWN_LEFT: [(0, 10), (20, 10), (20, 30), (10, 30), (10, 20), (0, 20)],
    TileType.UP_LEFT: [(10, 0), (20, 0), (20, 20), (0, 20), (0, 10), (10, 10)],
    TileType.UP_DOWN: [(10, 0), (20, 0), (20, 30), (10, 30)],
    TileType.RIGHT_LEFT: [(0, 10), (30, 10), (30, 20), (0, 20)],
    # three neighbors
    TileType.UP_RIGHT_DOWN: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30)],
    TileType.RIGHT_DOWN_LEFT: [(0, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 20), (0, 20)],
    TileType.UP_DOWN_LEFT: [(10, 0), (20, 0), (20, 30), (10, 30), (10, 20), (0, 20), (0, 10), (10, 10)],
    TileType.UP_RIGHT_LEFT: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (0, 20), (0, 10), (10, 10)],
    # four neighbors
    TileType.ALL: [(10, 0), (20, 0), (20, 10), (30, 10), (30, 20), (20, 20), (20, 30), (10, 30), (10, 20), (0, 20), (0, 10), (10, 10)],
}


def render_road_network(window, network, include_travel_paths=True):
    render_grid(window, network.grid)
    if include_travel_paths:
        render_travel_paths(window, network.graph)


#########
# Tiles #
#########

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


##############
# Road Graph #
##############

def tile_pos_to_pixel_center(pos: Tuple[int, int]):
    """Converts a tile position to the center pixel position for that tile"""
    r, c = pos
    return (c*TILE_WIDTH + TILE_WIDTH//2, r*TILE_HEIGHT + TILE_HEIGHT//2)


def render_node(window, pos: Tuple[int, int], color):
    center = tile_pos_to_pixel_center(pos)
    pygame.draw.circle(window, color, center, radius=3)


def render_edge(window, edge: Tuple[Tuple[int, int], Tuple[int, int]], color,
                width=1):
    a, b = edge
    center_a = tile_pos_to_pixel_center(a)
    center_b = tile_pos_to_pixel_center(b)
    pygame.draw.line(window, color, center_a, center_b, width=width)


def render_travel_paths(window, graph):
    """Draw lines to show intersection connections"""
    color = (255, 77, 255)  # pink
    # Draw nodes
    for n in graph.G.nodes:
        render_node(window, n, color)
    # Draw edges
    for a, b in graph.G.edges:
        render_edge(window, (a, b), color)


def render_path(window, path):
    """Render path from graph"""
    color = (0, 255, 0)  # green
    if len(path) < 2:
        return
    for idx in range(len(path)-1):
        edge = (path[idx], path[idx+1])
        render_edge(window, edge, color, width=10)
