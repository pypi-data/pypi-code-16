#!/usr/bin/env python

from __future__ import division

import math, pytest
from vecrec.shapes import *

def test_rectangle_accessor_methods():
    r = Rect(2, 4, 6, 8)
    s = Rect(1, 6, 8, 4)

    str(r)
    repr(r)

    assert r == r
    assert r == r.copy()
    assert r != None

    assert r.left == 2
    assert r.center_x == 5
    assert r.right == 8
    assert r.top == 12
    assert r.center_y == 8
    assert r.bottom == 4
    assert r.width == 6
    assert r.height == 8
    assert r.half_width == 3
    assert r.half_height == 4
    assert r.size == (6, 8)

    assert r.top_left == Vector(2, 12)
    assert r.top_center == Vector(5, 12)
    assert r.top_right == Vector(8, 12)
    assert r.center_left == Vector(2, 8)
    assert r.center == Vector(5, 8)
    assert r.center_right == Vector(8, 8)
    assert r.bottom_left == Vector(2, 4)
    assert r.bottom_center == Vector(5, 4)
    assert r.bottom_right == Vector(8, 4)
    assert r.vertices == (
            r.top_left, r.top_right, r.bottom_right, r.bottom_left)

    assert r.dimensions == ((2, 4), (6, 8))
    assert r.tuple == (2, 4, 6, 8)

    assert r.get_grown(1) == Rect(1, 3, 8, 10)
    assert r.get_shrunk(1) == Rect(3, 5, 4, 6)
    assert r.get_union(s) == Rect(1, 4, 8, 8)
    assert r.get_intersection(s) == Rect(2, 6, 6, 4)

def test_rectangle_mutator_methods():
    r = Rect(2, 2, 4, 4)
    q = Rect(1, 1, 6, 8)
    v = Vector(5, 6)

    assert r + v == Rect(7, 8, 4, 4)
    assert r - v == Rect(-3, -4, 4, 4)

    r += v;                     assert r == Rect(7, 8, 4, 4)
    r -= v;                     assert r == Rect(2, 2, 4, 4)

    r.grow(1);                  assert r == Rect(1, 1, 6, 6)
    r.shrink(1);                assert r == Rect(2, 2, 4, 4)

    r.align_left(q);            assert r == Rect(1, 2, 4, 4)
    r.align_center_x(q);        assert r == Rect(2, 2, 4, 4)
    r.align_right(q);           assert r == Rect(3, 2, 4, 4)
    r.align_top(q);             assert r == Rect(3, 5, 4, 4)
    r.align_center_y(q);        assert r == Rect(3, 3, 4, 4)
    r.align_bottom(q);          assert r == Rect(3, 1, 4, 4)

    r.set_width(6);             assert r == Rect(3, 1, 6, 4)
    r.set_height(7);            assert r == Rect(3, 1, 6, 7)
    r.set_size(4, 4);           assert r == Rect(3, 1, 4, 4)

    r.set_top_left(v);          assert r == Rect(5, 2, 4, 4)
    r.set_top_center(v);        assert r == Rect(3, 2, 4, 4)
    r.set_top_right(v);         assert r == Rect(1, 2, 4, 4)
    r.set_center_left(v);       assert r == Rect(5, 4, 4, 4)
    r.set_center(v);            assert r == Rect(3, 4, 4, 4)
    r.set_center_right(v);      assert r == Rect(1, 4, 4, 4)
    r.set_bottom_left(v);       assert r == Rect(5, 6, 4, 4)
    r.set_bottom_center(v);     assert r == Rect(3, 6, 4, 4)
    r.set_bottom_right(v);      assert r == Rect(1, 6, 4, 4)

    try: r.set_top_left(0)
    except VectorCastError: pass
    else: raise AssertionError

def test_rectangle_collision_methods():
        box = Rect(5, 5, 10, 10)

        class MyShape: pass
        shape = MyShape()

        pairs = [(x, y) for x in range(5)
                        for y in range(5)]

        box_contains = [
                [False, False, False, False, False],
                [False, True,  True,  True,  False],
                [False, True,  True,  True,  False],
                [False, True,  True,  True,  False],
                [False, False, False, False, False] ]

        minibox_inside = [
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, True,  False, False],
                [False, False, False, False, False],
                [False, False, False, False, False] ]

        minibox_touching = [
                [False, False, False, False, False],
                [False, True,  True,  True,  False],
                [False, True,  True,  True,  False],
                [False, True,  True,  True,  False],
                [False, False, False, False, False] ]

        for x, y in pairs:
            point = 5 * Vector(x, y)
            minibox = Rect.from_center(point, 4, 4)

            shape.bottom, shape.left = minibox.bottom_left
            shape.width, shape.height = minibox.size

            assert (point in box) == box_contains[y][x]
            assert box.contains(point) == box_contains[y][x]
            assert box.touching(point) == box_contains[y][x]

            assert (minibox in box) == minibox_inside[y][x]
            assert box.contains(minibox) == minibox_inside[y][x]
            assert box.touching(minibox) == minibox_touching[y][x]

            assert (shape in box) == minibox_inside[y][x]
            assert box.contains(shape) == minibox_inside[y][x]
            assert box.touching(shape) == minibox_touching[y][x]

            assert minibox.touching(box) == minibox_touching[y][x]
            assert minibox.inside(box) == minibox_inside[y][x]
            assert minibox.outside(box) == (not minibox_touching[y][x])

        try: box.inside(0)
        except RectangleCastError: pass
        else: raise AssertionError

        try: box.outside(0)
        except RectangleCastError: pass
        else: raise AssertionError

        try: box.touching(0)
        except RectangleCastError: pass
        else: raise AssertionError

        try: box.contains(0)
        except RectangleCastError: pass
        else: raise AssertionError

def test_rectangle_factory_methods():

    v = Vector(5, 6)
    t = 7, 8

    assert Rect.null() == Rect(0, 0, 0, 0)
    assert Rect.from_size(1, 2) == Rect(0, 0, 1, 2)
    assert Rect.from_width(3, ratio=2) == Rect(0, 0, 3, 6)
    assert Rect.from_height(4, ratio=2) == Rect(0, 0, 8, 4)
    assert Rect.from_vector(v) == Rect(5, 6, 0, 0)
    assert Rect.from_vector(t) == Rect(7, 8, 0, 0)
    assert Rect.from_square(9) == Rect(0, 0, 9, 9)
    assert Rect.from_dimensions(1, 2, 3, 4) == Rect(1, 2, 3, 4)
    assert Rect.from_sides(5, 7, 8, 6) == Rect(5, 6, 3, 1)
    assert Rect.from_corners((8, 4), (3, 1)) == Rect(3, 1, 5, 3)
    assert Rect.from_bottom_left(v, 1, 2) == Rect(5, 6, 1, 2)
    assert Rect.from_bottom_left(t, 3, 4) == Rect(7, 8, 3, 4)
    assert Rect.from_center(v, 8, 6) == Rect(1, 3, 8, 6)
    assert Rect.from_center(t, 4, 2) == Rect(5, 7, 4, 2)

    points = (1, 5), (0, 3), (4, 2), (6, 3), (5, 0)
    assert Rect.from_points(*points) == Rect(0, 0, 6, 5)

    a = Rect(1, 1, 4, 4)
    b = Rect(4, 4, 4, 4)

    assert Rect.from_union(a, b) == Rect(1, 1, 7, 7)
    assert Rect.from_intersection(a, b) == Rect(4, 4, 1, 1)

def test_rectangle_pickling():
    import pickle
    original_rect = Rect(2, 4, 6, 8)
    serialized_rect = pickle.dumps(original_rect)
    pickled_rect = pickle.loads(serialized_rect)
    assert original_rect == pickled_rect
    assert original_rect is not pickled_rect
