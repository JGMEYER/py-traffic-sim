import random
from enum import IntEnum
from typing import Dict, Tuple

import pygame
from pygame import sprite

from .common import (
    TileType,
    Update,
    grid_index_to_world_coords,
)
from .grid import RoadSegmentNode
from config import config


#############
# Constants #
#############


class Color:
    """Game colors"""

    BG = (255, 255, 255)  # white
    ROAD = (0, 0, 0)  # black
    TRAVEL_EDGE = (255, 77, 255)  # pink
    VEHICLE_DEFAULT = (255, 255, 0)  # yellow


class RoadScreenLayers(IntEnum):
    """Game screen layers

    0 = base layer. The higher the number to closer the sprite.
    """

    BG = 0
    TILES = 1
    TRAVEL_EDGES = 2
    ROAD_SEGMENT_NODES = 3
    VEHICLES = 4


##########
# Screen #
##########


class RoadScreen(sprite.LayeredDirty):
    """Manages all sprites for rendering a `RoadNetwork`.

    RoadScreen fetches updates from a network's components via get_updates()
    and updates their corresponding sprites accordingly.

    Sprites are grouped and layered to match the order of `RoadScreenLayers`.
    """

    def __init__(self, config, network):
        sprite.LayeredDirty.__init__(self)

        self.config = config

        self.w = network.w
        self.h = network.h
        self.network = network

        # Background
        self.bg = BackgroundSprite(
            config.TILE_WIDTH * self.w, config.TILE_HEIGHT * self.h
        )
        self.add(self.bg, layer=RoadScreenLayers.TILES)

        # Other sprite indexes
        self.tiles: Dict[Tuple[int, int], TileSprite] = {}
        self.edges: Dict[
            Tuple[RoadSegmentNode, RoadSegmentNode], TravelEdgeSprite
        ] = {}
        self.vehicles: Dict[int, VehicleSprite] = {}

    def update(self):
        """Update network sprites"""
        self._update_grid()
        self._update_graph()
        self._update_traffic()

    def _update_grid(self):
        """Update grid sprites with updates from network"""
        # TODO add way to change bg if tile is being moused over
        updates = self.network.grid.get_updates()

        # Update tiles
        for u_type, (r, c, tile_type) in updates:
            if u_type == Update.ADDED:
                sprite = TileSprite(self.config, r, c, tile_type)
                self.tiles[(r, c)] = sprite
                self.add(sprite, layer=RoadScreenLayers.TILES)

            elif u_type == Update.MODIFIED:
                self.tiles[(r, c)].update(r, c, tile_type)

    def _update_graph(self):
        """Update graph sprites with updates from network"""
        updates = self.network.graph.get_updates()

        # Update edges
        for u_type, (u_node, v_node) in updates:
            if u_type == Update.ADDED:
                sprite = TravelEdgeSprite(u_node, v_node)
                sprite.visible = self.config.DEBUG.DISPLAY_TRAVEL_EDGES
                self.edges[(u_node, v_node)] = sprite
                self.add(sprite, layer=RoadScreenLayers.TRAVEL_EDGES)

            elif u_type == Update.REMOVED:
                sprite = self.edges[(u_node, v_node)]
                self.remove(sprite)
                del self.edges[(u_node, v_node)]

    def _update_traffic(self):
        """Update traffic sprites with updates from network"""
        updates = self.network.traffic.get_updates()

        # Update vehicles
        for u_type, (id, x, y) in updates:
            if u_type == Update.ADDED:
                sprite = VehicleSprite(self.config, x, y)
                self.vehicles[id] = sprite
                self.add(sprite, layer=RoadScreenLayers.VEHICLES)

            elif u_type == Update.MODIFIED:
                self.vehicles[id].update(x, y)


###########
# Sprites #
###########


class BackgroundSprite(sprite.DirtySprite):
    """Background Sprite"""

    def __init__(self, w, h):
        sprite.DirtySprite.__init__(self)

        self.image, self.rect = self._image(w, h)

        # Required attributes to add to LayeredDirty
        self.dirty = 1
        self.visible = 1
        self.blendmode = 0

    def _image(self, w, h):
        """Create background image"""
        image = pygame.Surface([w, h])
        image.fill(Color.BG)

        rect = image.get_rect()
        rect.x, rect.y = (0, 0)

        return image, rect


class TileSprite(sprite.DirtySprite):
    """Sprite for a road tile"""

    def __init__(self, config, r, c, tile_type):
        sprite.DirtySprite.__init__(self)

        self.config = config

        self.r = r
        self.c = c

        self.image, self.rect = self._image(r, c, tile_type)

        # Required attributes to add to LayeredDirty
        self.dirty = 1
        self.visible = 1
        self.blendmode = 0

    def _image(self, r, c, tile_type, highlighted=False):
        """Create tile image"""
        image = pygame.Surface(
            [self.config.TILE_WIDTH, self.config.TILE_HEIGHT]
        )
        pygame.draw.polygon(image, Color.ROAD, TILE_POLYS[tile_type])

        rect = image.get_rect()
        rect.x, rect.y = grid_index_to_world_coords(
            config.TILE_WIDTH, config.TILE_HEIGHT, r, c
        )

        return image, rect

    def update(self, r, c, tile_type, highlighted=False):
        """Update tile type"""
        self.image, self.rect = self._image(r, c, tile_type)
        self.dirty = 1


class TravelEdgeSprite(sprite.DirtySprite):
    """Sprite for an edge on the travel graph"""

    LINE_WIDTH = 1

    def __init__(self, node_u, node_v):
        sprite.DirtySprite.__init__(self)

        self.image, self.rect = self._image(node_u, node_v)

        # Required attributes to add to LayeredDirty
        self.dirty = 1
        self.visible = 1
        self.blendmode = 0

    def _image(self, node_u, node_v):
        """Create edge image"""
        u_x, u_y = node_u.world_coords
        v_x, v_y = node_v.world_coords

        # Get dimensions of surface, making sure to save at least LINE_WIDTH
        # space for vertical and horizontal lines.
        w = max(int(abs(u_x - v_x)), self.LINE_WIDTH)
        h = max(int(abs(u_y - v_y)), self.LINE_WIDTH)

        # Get offset from (0, 0) to top left corner of surface
        x_offset, y_offset = min(u_x, v_x), min(u_y, v_y)

        # Get x and y values local to surface
        local_u_x, local_u_y = u_x - x_offset, u_y - y_offset
        local_v_x, local_v_y = v_x - x_offset, v_y - y_offset

        image = pygame.Surface([w, h])
        pygame.draw.line(
            image,
            Color.TRAVEL_EDGE,
            (local_u_x, local_u_y),
            (local_v_x, local_v_y),
            width=self.LINE_WIDTH,
        )

        rect = image.get_rect()
        rect.x, rect.y = x_offset, y_offset

        return image, rect


class VehicleSprite(sprite.DirtySprite):
    """Vehicle sprite"""

    def __init__(self, config, x, y):
        sprite.DirtySprite.__init__(self)

        self.config = config

        self.image, self.rect = self._image(
            x, y, config.RANDOMIZE_VEHICLE_COLOR
        )

        # Required attributes to add to LayeredDirty
        self.dirty = 1
        self.visible = 1
        self.blendmode = 0

    def _image(self, x, y, randomize_color):
        """Create vehicle image"""
        image = pygame.Surface(
            [
                self.config.VEHICLE_RADIUS * 2 + 1,
                self.config.VEHICLE_RADIUS * 2 + 1,
            ]
        )

        color = (
            random_color(150, 255)
            if randomize_color
            else Color.VEHICLE_DEFAULT
        )
        pygame.draw.circle(
            image,
            color,
            (self.config.VEHICLE_RADIUS, self.config.VEHICLE_RADIUS),
            radius=self.config.VEHICLE_RADIUS,
        )

        rect = image.get_rect()
        rect.x, rect.y = (
            x - self.config.VEHICLE_RADIUS,
            y - self.config.VEHICLE_RADIUS,
        )

        return image, rect

    def update(self, x, y):
        """Update vehicle location"""
        self.rect.x, self.rect.y = (
            x - self.config.VEHICLE_RADIUS,
            y - self.config.VEHICLE_RADIUS,
        )
        self.dirty = 1


def random_color(rgb_min, rgb_max):
    """Generate random color with each rgb channel between min/max range"""
    r = random.randint(rgb_min, rgb_max)
    g = random.randint(rgb_min, rgb_max)
    b = random.randint(rgb_min, rgb_max)
    return (r, g, b)


##############
# Tile Polys #
##############


def tile_poly(config, *, up=False, right=False, down=False, left=False):
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

    NOTE:

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
    tw, th = config.TILE_WIDTH, config.TILE_HEIGHT
    rw = config.ROAD_WIDTH

    points = []

    if up:
        points.extend(
            [
                (tw // 2 - (rw // 2 - 1), 0),
                ((tw // 2 + 1) + (rw // 2 - 1), 0),
                ((tw // 2 + 1) + (rw // 2 - 1), th // 2 - (rw // 2 - 1)),
            ]
        )
    else:
        points.extend(
            [((tw // 2 + 1) + (rw // 2 - 1), th // 2 - (rw // 2 - 1))]
        )

    if right:
        points.extend(
            [
                (tw - 1, th // 2 - (rw // 2 - 1)),
                (tw - 1, (th // 2 + 1) + (rw // 2 - 1)),
                ((tw // 2 + 1) + (rw // 2 - 1), (th // 2 + 1) + (rw // 2 - 1)),
            ]
        )
    else:
        points.extend(
            [((tw // 2 + 1) + (rw // 2 - 1), (th // 2 + 1) + (rw // 2 - 1))]
        )

    if down:
        points.extend(
            [
                ((tw // 2 + 1) + (rw // 2 - 1), th - 1),
                (tw // 2 - (rw // 2 - 1), th - 1),
                (tw // 2 - (rw // 2 - 1), (th // 2 + 1) + (rw // 2 - 1)),
            ]
        )
    else:
        points.extend(
            [(tw // 2 - (rw // 2 - 1), (th // 2 + 1) + (rw // 2 - 1))]
        )

    if left:
        points.extend(
            [
                (0, (th // 2 + 1) + (rw // 2 - 1)),
                (0, th // 2 - (rw // 2 - 1)),
                (tw // 2 - (rw // 2 - 1), th // 2 - (rw // 2 - 1)),
            ]
        )
    else:
        points.extend([(tw // 2 - (rw // 2 - 1), th // 2 - (rw // 2 - 1))])

    return points


# NOTE: We pass config directly here just to get this working. In the future,
# we'll want to rethink how values are passed via config, so it may be worth
# reworking how we pass config here.
TILE_POLYS = {
    # no tile
    TileType.EMPTY: [],
    # no neighbors
    TileType.ALONE: tile_poly(config),
    # one neighbor
    TileType.UP: tile_poly(config, up=True),
    TileType.RIGHT: tile_poly(config, right=True),
    TileType.DOWN: tile_poly(config, down=True),
    TileType.LEFT: tile_poly(config, left=True),
    # two neighbors
    TileType.UP_RIGHT: tile_poly(config, up=True, right=True),
    TileType.RIGHT_DOWN: tile_poly(config, right=True, down=True),
    TileType.DOWN_LEFT: tile_poly(config, down=True, left=True),
    TileType.UP_LEFT: tile_poly(config, up=True, left=True),
    TileType.UP_DOWN: tile_poly(config, up=True, down=True),
    TileType.RIGHT_LEFT: tile_poly(config, right=True, left=True),
    # three neighbors
    TileType.UP_RIGHT_DOWN: tile_poly(config, up=True, right=True, down=True),
    TileType.RIGHT_DOWN_LEFT: tile_poly(
        config, right=True, down=True, left=True
    ),
    TileType.UP_DOWN_LEFT: tile_poly(config, up=True, down=True, left=True),
    TileType.UP_RIGHT_LEFT: tile_poly(config, up=True, right=True, left=True),
    # four neighbors
    TileType.UP_RIGHT_DOWN_LEFT: tile_poly(
        config, up=True, right=True, down=True, left=True
    ),
}
