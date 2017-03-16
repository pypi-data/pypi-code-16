#!/usr/bin/env python

from __future__ import division

import pytest
from vecrec import Shape

def test_shape_interface():
    class MyShape (Shape): pass
    shape = MyShape()

    with pytest.raises(NotImplementedError):
        shape.bottom
    with pytest.raises(NotImplementedError):
        shape.left
    with pytest.raises(NotImplementedError):
        shape.width
    with pytest.raises(NotImplementedError):
        shape.height

