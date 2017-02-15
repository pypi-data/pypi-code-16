# -*- coding: utf-8 -*-

from permoize.core import qualified_name, permoize


def test_qualified_name():
    assert qualified_name(qualified_name) == 'permoize.core.qualified_name'


def test_everything(tmpdir):
    @permoize(tmpdir.dirname, True)
    def fn_1(x, y=2, z=3, *args, **kwargs):
        return sum([x, y, z] + list(args) + list(kwargs.values()))

    assert fn_1(1) == (6, True)
    assert fn_1(1) == (6, False)

    assert fn_1(1, 3) == (7, True)
    assert fn_1(1, 3) == (7, False)

    assert fn_1(1, 3, 4) == (8, True)
    assert fn_1(1, 3, 4) == (8, False)

    assert fn_1(1, a=1) == (7, True)
    assert fn_1(1, a=1) == (7, False)

    assert fn_1(1, b=1) == (7, True)
    assert fn_1(1, b=1) == (7, False)

    assert fn_1(1, 2, 3, 1) == (7, True)
    assert fn_1(1, 2, 3, 1) == (7, False)

    assert fn_1(1, 2, 3, 1, c=1) == (8, True)
    assert fn_1(1, 2, 3, 1, c=1) == (8, False)
