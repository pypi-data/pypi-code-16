import typing

from .sentiment_analysis import *


def test_def_read_file():
    assert isinstance(def_read_file(), typing.Callable)
