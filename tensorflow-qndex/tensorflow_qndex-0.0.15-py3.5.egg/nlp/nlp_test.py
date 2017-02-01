import typing

from .nlp import *


def test_def_char_file():
    add_char_file_flag()


def test_def_word_file():
    add_word_file_flag()


def test_def_word_array():
    assert isinstance(def_word_array(), typing.Callable)
