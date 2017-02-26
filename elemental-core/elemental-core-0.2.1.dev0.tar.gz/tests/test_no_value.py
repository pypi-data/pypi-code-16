import weakref

import elemental_core


def test_bool():
    assert not elemental_core.NO_VALUE


def test_weak_ref():
    ref = weakref.ref(elemental_core.NO_VALUE)
    assert ref
    assert ref() is elemental_core.NO_VALUE
