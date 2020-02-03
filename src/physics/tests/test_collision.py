import pytest
from pygame import Rect

from physics.collision import CollisionTileGrid


def test__get_corners():
    ctg = CollisionTileGrid(3, 3, 2, 2)
    c_obj = Rect((1, 1), (2, 2))
    corners = ctg._get_corners(c_obj)
    assert corners == [(1, 1), (3, 1), (3, 3), (1, 3)]


def test__get_occupied_tiles():
    ctg = CollisionTileGrid(3, 3, 2, 2)

    # Obj with dimensions <= tile dimensions
    tiles = ctg._get_occupied_tiles(Rect((1, 1), (2, 2)))
    assert tiles == {(0, 0), (0, 1), (1, 1), (1, 0)}

    # Obj with dimensions > tile dimensions
    tiles = ctg._get_occupied_tiles(Rect((1, 1), (4, 4)))
    assert tiles == {(0, 0), (0, 1), (0, 2),
                     (1, 0), (1, 1), (1, 2),
                     (2, 0), (2, 1), (2, 2)}

    # Rectangular obj
    tiles = ctg._get_occupied_tiles(Rect((3, 1), (2, 4)))
    assert tiles == {(0, 1), (0, 2),
                     (1, 1), (1, 2),
                     (2, 1), (2, 2)}


def test_update_object():
    ctg = CollisionTileGrid(3, 3, 2, 2)

    # Add new obj 1
    ctg.update_object(1, Rect((1, 1), (2, 2)))
    assert ctg.obj2tiles == {1: {(0, 0), (0, 1), (1, 1), (1, 0)}}
    assert ctg.tile2objs == {
                                (0, 0): {1},
                                (0, 1): {1},
                                (0, 2): set(),
                                (1, 0): {1},
                                (1, 1): {1},
                                (1, 2): set(),
                                (2, 0): set(),
                                (2, 1): set(),
                                (2, 2): set(),
                            }

    # Add new obj 2
    ctg.update_object(2, Rect((2, 2), (1, 1)))
    assert ctg.obj2tiles == {
                                1: {(0, 0), (0, 1), (1, 1), (1, 0)},
                                2: {(1, 1)},
                            }
    assert ctg.tile2objs == {
                                (0, 0): {1},
                                (0, 1): {1},
                                (0, 2): set(),
                                (1, 0): {1},
                                (1, 1): {1, 2},
                                (1, 2): set(),
                                (2, 0): set(),
                                (2, 1): set(),
                                (2, 2): set(),
                            }

    # Move obj 2
    ctg.update_object(2, Rect((1, 1), (1, 1)))
    assert ctg.obj2tiles == {
                                1: {(0, 0), (0, 1), (1, 1), (1, 0)},
                                2: {(0, 0), (0, 1), (1, 1), (1, 0)},
                            }
    assert ctg.tile2objs == {
                                (0, 0): {1, 2},
                                (0, 1): {1, 2},
                                (0, 2): set(),
                                (1, 0): {1, 2},
                                (1, 1): {1, 2},
                                (1, 2): set(),
                                (2, 0): set(),
                                (2, 1): set(),
                                (2, 2): set(),
                            }


def test_remove_object():
    ctg = CollisionTileGrid(3, 3, 2, 2)

    with pytest.raises(KeyError):
        ctg.remove_object(1)
    with pytest.raises(KeyError):
        ctg.remove_object(2)

    ctg.update_object(1, Rect((1, 1), (2, 2)))
    ctg.update_object(2, Rect((2, 2), (1, 1)))

    ctg.remove_object(1)
    ctg.remove_object(2)

    assert ctg.obj2tiles == {}
    assert ctg.tile2objs == {
                                (0, 0): set(),
                                (0, 1): set(),
                                (0, 2): set(),
                                (1, 0): set(),
                                (1, 1): set(),
                                (1, 2): set(),
                                (2, 0): set(),
                                (2, 1): set(),
                                (2, 2): set(),
                            }

    with pytest.raises(KeyError):
        ctg.remove_object(1)
    with pytest.raises(KeyError):
        ctg.remove_object(2)


def test__nearby_objects():
    ctg = CollisionTileGrid(3, 3, 2, 2)

    ctg.update_object(1, Rect((1, 1), (2, 2)))
    ctg.update_object(2, Rect((2, 2), (1, 1)))

    assert ctg._nearby_objects(1) == {2}
    assert ctg._nearby_objects(2) == {1}

    ctg.update_object(3, Rect((0, 0), (2, 2)))
    ctg.update_object(4, Rect((4, 4), (1, 1)))

    assert ctg._nearby_objects(1) == {2, 3}
    assert ctg._nearby_objects(2) == {1, 3}
    assert ctg._nearby_objects(3) == {1, 2}
    assert ctg._nearby_objects(4) == set()


def test_colliding_objects():
    # TODO implement this
    pass
