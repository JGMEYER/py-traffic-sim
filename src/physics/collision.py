from abc import ABC, abstractmethod
from typing import Dict, Set, Tuple

from pygame import Rect


class Collidable(ABC):
    """A class that can collide with other objects."""

    @abstractmethod
    def get_collision_rect() -> Rect:
        """Return collision box for the object as a Rect."""
        raise NotImplementedError


class CollisionTileGrid():
    """A grid of collision objects for efficiently determining collisions
    between the objects.
    """

    def __init__(self, cgrid_width, cgrid_height, ctile_width, ctile_height):
        self.ctg_gw = cgrid_width
        self.ctg_gh = cgrid_height
        self.ctg_tw = ctile_width
        self.ctg_th = ctile_height

        self.objs: Dict[int, Rect] = {}
        self.obj2tiles: Dict[int, Set[Tuple[int, int]]] = {}
        self.tile2objs: Dict[Tuple[int, int], Set[int]] = {}

        for r in range(cgrid_height):
            for c in range(cgrid_width):
                self.tile2objs[(r, c)] = set()

    def update_object(self, obj_id, c_obj: Rect):
        """Updates a collision object's location and dimensions within the
        collision grid. Creates a new object with the provided obj_id if one
        does not already exist.

        Rect x and y coordinates should correspond with world coordinates on
        the grid.
        """
        self.objs[obj_id] = c_obj

        old_tiles = self.obj2tiles.get(obj_id)
        if old_tiles:
            for r, c in old_tiles:
                self.tile2objs[(r, c)].remove(obj_id)

        new_tiles = self._get_occupied_tiles(c_obj)
        for r, c in new_tiles:
            self.tile2objs[(r, c)].add(obj_id)
        self.obj2tiles[obj_id] = new_tiles

    def remove_object(self, obj_id):
        """Removes existing object from the collision grid."""
        tiles = self.obj2tiles[obj_id]
        for r, c in tiles:
            self.tile2objs[(r, c)].remove(obj_id)
        del self.obj2tiles[obj_id]
        del self.objs[obj_id]

    def has_collision(self, obj_id):
        """Returns True if object is colliding with another object in the grid.
        """
        c_obj = self.objs[obj_id]

        for nearby_obj_id in self._nearby_objects(obj_id):
            nearby_obj = self.objs[nearby_obj_id]
            if c_obj.colliderect(nearby_obj):
                return True

        return False

    def colliding_object_ids(self, obj_id):
        """Returns ids of objects colliding with the provided object."""
        colliding_obj_ids = set()
        c_obj = self.objs[obj_id]

        for nearby_obj_id in self._nearby_objects(obj_id):
            nearby_obj = self.objs[nearby_obj_id]
            if c_obj.colliderect(nearby_obj):
                colliding_obj_ids.add(nearby_obj_id)

        return colliding_obj_ids

    def _nearby_objects(self, obj_id):
        """Returns ids of objects sharing tiles with object of provided id."""
        collision_ids = set()

        obj_tiles = self.obj2tiles[obj_id]
        for r, c in obj_tiles:
            collision_ids.update(self.tile2objs[(r, c)])

        collision_ids.remove(obj_id)

        return collision_ids

    def _get_corners(self, c_obj: Rect):
        """Returns corners bounding the collision object.

        NOTE: If this needs to be reused, we could extend pygame.Rect and add
        this function to the new class.
        """
        return [
            c_obj.topleft, c_obj.topright, c_obj.bottomright, c_obj.bottomleft,
        ]

    def _get_occupied_tiles(self, c_obj: Rect):
        """Returns all tiles occupied by an object with the provided location
        and dimensions"""
        tiles = set()

        rows = set()
        cols = set()

        corners = self._get_corners(c_obj)

        for x, y in corners:
            r, c = self._world_coords_to_tile_index(x, y)
            rows.add(r)
            cols.add(c)

        for r in range(min(rows), max(rows)+1):
            for c in range(min(cols), max(cols)+1):
                tiles.add((r, c))

        return tiles

    def _world_coords_to_tile_index(self, x: float, y: float):
        """Convert (x, y) coordinate on the world plane to the corresponding
        (row, col) index on the grid.

        NOTE: If this functionality needs to be reused in this module, consider
        moving it to a common.py or similar.
        """
        return (y//self.ctg_th, x//self.ctg_tw)
