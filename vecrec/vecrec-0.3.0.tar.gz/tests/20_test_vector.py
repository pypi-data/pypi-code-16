#!/usr/bin/env python

from __future__ import division

import math, pytest
from vecrec.shapes import *

def test_vector_accessor_methods():
    v = Vector(3, 4)
    w = Vector(3.5, 4.5)
    x = Vector(3, -4)

    str(v)
    repr(v)

    assert v.x == 3
    assert v.y == 4
    assert v.xy == (3, 4)
    assert v.tuple == (3, 4)
    assert v.magnitude == 5.0
    assert v.magnitude_squared == 25
    assert v.unit == Vector(3, 4) / 5.0
    assert v.orthogonal == Vector(-4, 3)
    assert v.orthonormal == Vector(-4, 3) / 5.0
    assert 0.92 < v.radians < 0.93
    assert 53.1 < v.degrees < 53.2
    assert -0.93 < x.radians < -0.92
    assert -53.2 < x.degrees < -53.1
    assert sum([v, x]) == Vector(6, 0)

    a, b = v
    assert a == 3 and b == 4

    v.x = 1;            assert v.x == 1
    v.y = 2;            assert v.y == 2
    v.xy = 5,6;         assert v.x == 5 and v.y == 6
    v.tuple = 3, 4;     assert v.x == 3 and v.y == 4
    v.magnitude = 1
    v.radians = 0;      assert 0.99 < v.x < 1.01 and -0.01 < v.y < 0.01
    v.degrees = 90;     assert -0.01 < v.x < 0.01 and 0.99 < v.y < 1.01
    v.set_x(7);         assert v.get_x() == 7
    v.set_y(8);         assert v.get_y() == 8

def test_vector_overloaded_operators():
    r = Vector(4, 6)
    s = Vector(2, 2)
    t = (2, 2); k = 2

    class VectorLike: pass


    u = VectorLike()
    u.x = 2
    u.y = 2

    # Hard-coded operators

    assert r[0] == 4
    assert r[1] == 6
    assert -r == Vector(-4, -6)
    assert abs(r) == Vector(4, 6)
    assert bool(r)

    # Equality operators

    assert r == r
    assert r == (4, 6)
    assert (4, 6) == r

    assert r != s
    assert r != t
    assert r != u
    assert s != r
    assert t != r
    assert u != r
    assert r != None

    # Addition operator
    
    assert r + s == Vector(6, 8)
    assert r + t == Vector(6, 8)
    assert r + u == Vector(6, 8)
    assert s + r == Vector(6, 8)
    assert t + r == Vector(6, 8)
    assert u + r == Vector(6, 8)

    try: r + k
    except VectorCastError: pass
    else: raise AssertionError

    try: k + r
    except VectorCastError: pass
    else: raise AssertionError

    # Subtraction operator
    
    assert r - s == Vector(2, 4)
    assert r - t == Vector(2, 4)
    assert r - u == Vector(2, 4)
    assert s - r == Vector(-2, -4)
    assert t - r == Vector(-2, -4)
    assert u - r == Vector(-2, -4)

    try: r - k
    except VectorCastError: pass
    else: raise AssertionError

    try: k - r
    except VectorCastError: pass
    else: raise AssertionError

    # Multiplication operator
    
    assert r * s == Vector(8, 12)
    assert r * t == Vector(8, 12)
    assert r * k == Vector(8, 12)
    assert s * r == Vector(8, 12)
    assert t * r == Vector(8, 12)
    assert k * r == Vector(8, 12)

    # Division operators
    
    assert r / s == Vector(2, 3)
    assert r / t == Vector(2, 3)
    assert r / k == Vector(2, 3)
    assert s / r == Vector(1/2, 1/3)
    assert t / r == Vector(1/2, 1/3)
    assert k / r == Vector(1/2, 1/3)

    assert r // s == Vector(2, 3)
    assert r // t == Vector(2, 3)
    assert r // k == Vector(2, 3)
    assert s // r == Vector(0, 0)
    assert t // r == Vector(0, 0)
    assert k // r == Vector(0, 0)

    assert r % s == Vector(0, 0)
    assert r % t == Vector(0, 0)
    assert r % k == Vector(0, 0)
    assert s % r == Vector(2, 2)
    assert t % r == Vector(2, 2)
    assert k % r == Vector(2, 2)

    # Exponent operator

    assert r ** s == Vector(16, 36)
    assert r ** t == Vector(16, 36)
    assert r ** k == Vector(16, 36)
    assert s ** r == Vector(16, 64)
    assert t ** r == Vector(16, 64)
    assert k ** r == Vector(16, 64)

    # In-place operators

    r = Vector(4, 6)

    r += s;     assert r == Vector(6, 8)
    r -= s;     assert r == Vector(4, 6)
    r *= s;     assert r == Vector(8, 12)
    r /= s;     assert r == Vector(4, 6)
    r //= s;    assert r == Vector(2, 3)
    r %= s;     assert r == Vector(0, 1)
    r **= s;    assert r == Vector(0, 1)

    r = Vector(4, 6)

    r += t;     assert r == Vector(6, 8)
    r -= t;     assert r == Vector(4, 6)
    r *= t;     assert r == Vector(8, 12)
    r /= t;     assert r == Vector(4, 6)
    r //= t;    assert r == Vector(2, 3)
    r %= t;     assert r == Vector(0, 1)
    r **= t;    assert r == Vector(0, 1)

    r = Vector(4, 6)

    r += u;     assert r == Vector(6, 8)
    r -= u;     assert r == Vector(4, 6)
    r *= u;     assert r == Vector(8, 12)
    r /= u;     assert r == Vector(4, 6)
    r //= u;    assert r == Vector(2, 3)
    r %= u;     assert r == Vector(0, 1)
    r **= u;    assert r == Vector(0, 1)

    r = Vector(4, 6)

    r *= k;     assert r == Vector(8, 12)
    r /= k;     assert r == Vector(4, 6)
    r //= k;    assert r == Vector(2, 3)
    r %= k;     assert r == Vector(0, 1)
    r **= k;    assert r == Vector(0, 1)

    try: r += k
    except VectorCastError: pass
    else: raise AssertionError

    try: r -= k
    except VectorCastError: pass
    else: raise AssertionError

    r = Vector(4, 6)

    r += 0;     assert r == Vector(4, 6)
    r -= 0;     assert r == Vector(4, 6)
    r *= 0;     assert r == Vector(0, 0)
    r **= 0;    assert r == Vector(1, 1)

    try: r / 0
    except: ZeroDivisionError
    else: raise AssertionError

    try: r // 0
    except: ZeroDivisionError
    else: raise AssertionError

    try: r % 0
    except: ZeroDivisionError
    else: raise AssertionError

def test_vector_math_methods():

    r = Vector(4, 5)
    s = Vector(1, 1)
    t = (1, 1)

    assert r.get_distance(s) == 5
    assert r.get_distance(t) == 5
    assert r.get_manhattan(s) == 7
    assert r.get_manhattan(t) == 7

    r = Vector(3, 4)
    r.normalize()

    assert r == Vector(3, 4) / 5.0

    try: Vector.null().normalize()
    except NullVectorError: pass

    r = Vector(3, 4)

    s = r.get_scaled(10)
    r.scale(10)

    assert r == Vector(6, 8)
    assert s == Vector(6, 8)

    q = Vector(1, 2)
    r = Vector(1, 2)
    s = Vector(1, 4)
    t = (1, 4)

    assert q.get_interpolated(s, 0.5) == Vector(1, 3)
    assert q.get_interpolated(t, 0.5) == Vector(1, 3)
    assert interpolate(q, q, 3) == [q, q, q]
    assert interpolate(q, s, 3) == [q, Vector(1, 3), s]

    q.interpolate(s, 0.5)
    r.interpolate(t, 0.5)

    assert q == Vector(1, 3)
    assert r == Vector(1, 3)

    r = Vector(3, 4)
    s = Vector(2, 3)

    assert r.dot_product(s) == r.dot(s) == 18
    assert r.perp_product(s) == r.perp(s) == 1

    r = Vector(2, 2)
    s = Vector(5, 0)
    t = (5, 0)

    u = r.get_projection(s)
    v = r.get_projection(t)
    x, y = r.get_components(s)
    w, z = r.get_components(t)

    assert u == Vector(2, 0) and v == Vector(2, 0)
    assert x == Vector(0, 2) and y == Vector(2, 0)
    assert w == Vector(0, 2) and z == Vector(2, 0)

    q = Vector(2, 2)
    r = Vector(2, 2)
    s = Vector(5, 0)
    t = (5, 0)

    q.project(s)
    r.project(t)

    assert q == Vector(2, 0)
    assert r == Vector(2, 0)

    r = Vector(1, 0)
    s = Vector(0, 1)
    z = Vector.null()

    assert r.get_degrees_to(r) == 0
    assert r.get_radians_to(r) == 0
    assert r.get_degrees_to(s) == 90
    assert s.get_degrees_to(r) == -90
    assert r.get_radians_to(s) == math.pi / 2
    assert s.get_radians_to(r) == -math.pi / 2

    with pytest.raises(NullVectorError):
        z.get_radians()
    
def test_vector_factory_methods():
    assert Vector.null() == Vector(0, 0)
    assert Vector.from_tuple((3, 4)) == Vector(3, 4)
    assert Vector.from_scalar(2) == Vector(2, 2)

    v = Vector(3, 4)
    r = v.copy()
    s = Vector.null()
    s.assign(v)

    assert v == r
    assert v == s
    assert v is not r
    assert v is not s

    # Angle-based factories

    degrees = [0, 90, 180, 270]
    radians = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
    vectors = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    for d, r, v in zip(degrees, radians, vectors):
        assert Vector.from_radians(r).get_distance(v) < 1e-5
        assert Vector.from_degrees(d).get_distance(v) < 1e-5

    # Randomized factories

    n = 1000
    tolerance = 3 * math.sqrt(n)
    box = Rect.from_center((0, 0), 1, 1)

    circle_vectors = [Vector.random() for x in range(n)]
    rectangle_vectors = [Vector.from_rectangle(box) for x in range(n)]
    circle_deviation = sum(circle_vectors).magnitude
    rectangle_deviation = sum(rectangle_vectors).magnitude

    try:
        assert circle_deviation < tolerance
        assert rectangle_deviation < tolerance

    except AssertionError:
        print("The random vector factory test are not deterministic, and will ")
        print("spuriously fail roughly 0.01% of the time.  This could be the ")
        print("cause of the current failure, especially if the factory code ")
        print("has not been changed recently.  Try running the test again.")
        raise

def test_vector_pickling():
    import pickle
    original_vector = Vector(3, 4)
    serialized_vector = pickle.dumps(original_vector)
    pickled_vector = pickle.loads(serialized_vector)
    assert original_vector == pickled_vector
    assert original_vector is not pickled_vector

