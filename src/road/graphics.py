from typing import Tuple

import pygame

from .constants import (
    TILE_WIDTH as tw,
    TILE_HEIGHT as th,
    ROAD_WIDTH as rw,
    TileType,
)


def render_road_network(window, network, include_travel_paths=True):
    render_grid(window, network.grid)
    if include_travel_paths:
        render_travel_paths(window, network.graph)
    render_traffic(window, network.traffic)


#########
# Tiles #
#########

def tile_poly(up=False, right=False, down=False, left=False):
    """Construct polygon based on road connections.

    The calculations of these point locations depends on the width and height
    of our tiles as well as the width of our roads.

    To do this we step through each road direction clockwise, starting with UP.
    We then add a certain number of points to the polygon for each direction
    depending on whether the tile contains a road for the specified direction.

    Take for example an UP_DOWN_LEFT road tile:

        ┌───┬───┬───┬───┐
        │   │ * │ * │   │
        ├───┼───┼───┼───┤
        │ * │ * │ * │   │
        ├───┼───┼───┼───┤
        │ * │ * │ * │   │
        ├───┼───┼───┼───┤
        │   │ * │ * │   │
        └───┴───┴───┴───┘

    Each cell in the grid represents a point along the road tile, not a pixel
    on the final rendered tile. Though, if it's helpful, you can also imagine
    these represent a 4x4 pixel tile with a road width of 2.

    We determine these points through the following steps:

    STEP 1: UP

        ┌───┬───┬───┬───┐
        │   │ 0 │ 1 │   │
        ├───┼───┼───┼───┤
        │   │ x │ 2 │   │
        ├───┼───┼───┼───┤
        │   │   │   │   │
        ├───┼───┼───┼───┤
        │   │   │   │   │
        └───┴───┴───┴───┘

        An UP_DOWN_LEFT tile has a road going in the UP direction, so we add
        the 3 numbered points shown.

        As we step through each direction, we don't care about the "clockwise"-
        most point as we traverse the perimeter of the road. These will be
        filled in either the previous or future steps. The point marked with an
        'x', for example, will later be added in the LEFT step.

    STEP 2: RIGHT

        ┌───┬───┬───┬───┐
        │   │   │   │   │
        ├───┼───┼───┼───┤
        │   │   │ x │   │
        ├───┼───┼───┼───┤
        │   │   │ 3 │   │
        ├───┼───┼───┼───┤
        │   │   │   │   │
        └───┴───┴───┴───┘

        An UP_DOWN_LEFT tile does NOT have a road going in the RIGHT direction,
        so we add the 1 point shown.

        The point marked with an 'x' has already been added in our previous UP
        step and therefore no longer needs to be added to complete our polygon.

    STEP 3: DOWN

        ┌───┬───┬───┬───┐
        │   │   │   │   │
        ├───┼───┼───┼───┤
        │   │   │   │   │
        ├───┼───┼───┼───┤
        │   │ 6 │   │   │
        ├───┼───┼───┼───┤
        │   │ 5 │ 4 │   │
        └───┴───┴───┴───┘

        An UP_DOWN_LEFT tile has a road going in the DOWN direction, so we add
        the 3 points shown.

    STEP 4: LEFT

        ┌───┬───┬───┬───┐
        │   │   │   │   │
        ├───┼───┼───┼───┤
        │ 8 │ 9 │   │   │
        ├───┼───┼───┼───┤
        │ 7 │   │   │   │
        ├───┼───┼───┼───┤
        │   │   │   │   │
        └───┴───┴───┴───┘

        An UP_DOWN_LEFT tile has a road going in the LEFT direction, so we add
        the 3 points above.

        We now have a set of points that matches our first illustration.

    In summary, we add either 1 or 3 points depending on whether the road tile
    has a road segment going in a particular direction. We only include points
    necessary to complete to polygon and to avoid redundancy.

    IMPORTANT NOTE:

    This strategy creates redundant points on fully straight edges. e.g. an
    UP_DOWN_LEFT tile really only needs the following points to render:

        ┌───┬───┬───┬───┐
        │   │ * │ * │   │
        ├───┼───┼───┼───┤
        │ * │ * │   │   │
        ├───┼───┼───┼───┤
        │ * │ * │   │   │
        ├───┼───┼───┼───┤
        │   │ * │ * │   │
        └───┴───┴───┴───┘

    However, this strategy was done to keep the logic simple and to iterate
    quickly on adding tiles with dynamic sizes. If needed, this can be
    optimized later.
    """
    points = []

    if up:
        points.extend(
            [(tw//2-(rw//2-1), 0),
             ((tw//2+1)+(rw//2-1), 0),
             ((tw//2+1)+(rw//2-1), th//2-(rw//2-1))])
    else:
        points.extend(
            [((tw//2+1)+(rw//2-1), th//2-(rw//2-1))])

    if right:
        points.extend(
            [(tw-1, th//2-(rw//2-1)),
             (tw-1, (th//2+1)+(rw//2-1)),
             ((tw//2+1)+(rw//2-1), (th//2+1)+(rw//2-1))])
    else:
        points.extend(
            [((tw//2+1)+(rw//2-1), (th//2+1)+(rw//2-1))])

    if down:
        points.extend(
            [((tw//2+1)+(rw//2-1), th-1),
             (tw//2-(rw//2-1), th-1),
             (tw//2-(rw//2-1), (th//2+1)+(rw//2-1))])
    else:
        points.extend(
            [(tw//2-(rw//2-1), (th//2+1)+(rw//2-1))])

    if left:
        points.extend(
            [(0, (th//2+1)+(rw//2-1)),
             (0, th//2-(rw//2-1)),
             (tw//2-(rw//2-1), th//2-(rw//2-1))])
    else:
        points.extend(
            [(tw//2-(rw//2-1), th//2-(rw//2-1))])

    return points


TILE_POLYS = {
    # no tile
    TileType.EMPTY: [],
    # no neighbors
    TileType.ALONE: tile_poly(),
    # one neighbor
    TileType.UP: tile_poly(up=True),
    TileType.RIGHT: tile_poly(right=True),
    TileType.DOWN: tile_poly(down=True),
    TileType.LEFT: tile_poly(left=True),
    # two neighbors
    TileType.UP_RIGHT: tile_poly(up=True, right=True),
    TileType.RIGHT_DOWN: tile_poly(right=True, down=True),
    TileType.DOWN_LEFT: tile_poly(down=True, left=True),
    TileType.UP_LEFT: tile_poly(up=True, left=True),
    TileType.UP_DOWN: tile_poly(up=True, down=True),
    TileType.RIGHT_LEFT: tile_poly(right=True, left=True),
    # three neighbors
    TileType.UP_RIGHT_DOWN: tile_poly(up=True, right=True, down=True),
    TileType.RIGHT_DOWN_LEFT: tile_poly(right=True, down=True, left=True),
    TileType.UP_DOWN_LEFT: tile_poly(up=True, down=True, left=True),
    TileType.UP_RIGHT_LEFT: tile_poly(up=True, right=True, left=True),
    # four neighbors
    TileType.ALL: tile_poly(up=True, right=True, down=True, left=True)
}


def render_tile(window, r, c, road_type):
    """Draw single road tile to window"""
    points = TILE_POLYS[road_type]
    if not points:
        return
    translated_points = [(x + tw * c, y + th * r)
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
    return (c*tw + tw//2, r*th + th//2)


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


############
# Vehicles #
############

def render_vehicle(window, vcl):
    """Render vehicle"""
    x, y = vcl.world_coords
    pygame.draw.circle(window, (255, 255, 0), (round(x), round(y)), radius=8)


def render_traffic(window, traffic):
    """Render all vehicles"""
    for v in traffic.vehicles:
        render_vehicle(window, v)
