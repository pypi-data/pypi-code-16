import typing

from .classify import *


def test_def_classify():
    assert isinstance(def_classify(), typing.Callable)
