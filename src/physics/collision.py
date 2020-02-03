from typing import Dict, Set, Tuple

from pygame import Rect


class CollisionTileGrid():
    """A grid of collision objects with locations and dimensions for
    efficiently determining collisions between the objects."""

    def __init__(self, cgrid_width, cgrid_height, ctile_width, ctile_height):
        self.ctg_gw = cgrid_width
        self.ctg_gh = cgrid_height
        self.ctg_tw = ctile_width
        self.ctg_th = ctile_height

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

    def colliding_objects(self, obj_id):
        """Returns ids of objects colliding with the provided object."""
        # TODO -- return list of objects colliding with current object
        #      -- use nearby_objects to limit search
        pass

    def _nearby_objects(self, obj_id):
        """Returns ids of objects sharing tiles with object of provided id."""
        collision_ids = set()

        obj_tiles = self.obj2tiles[obj_id]
        for r, c in obj_tiles:
            collision_ids.update(self.tile2objs[(r, c)])

        collision_ids.remove(obj_id)

        return collision_ids

    def _get_corners(self, c_obj: Rect):
        """Returns corners bounding an object with the provided location and
        dimensions."""
        corners = [
            (c_obj.x, c_obj.y),  # upper left
            (c_obj.x + c_obj.width, c_obj.y),  # upper right
            (c_obj.x + c_obj.width, c_obj.y + c_obj.height),  # bottom right
            (c_obj.x, c_obj.y + c_obj.height),  # bottom left
        ]
        return corners

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
        # TODO should this really be here?
        """Convert (x, y) coordinate on the world plane to the corresponding
        (row, col) index on the grid.
        """
        return (y//self.ctg_th, x//self.ctg_tw)
