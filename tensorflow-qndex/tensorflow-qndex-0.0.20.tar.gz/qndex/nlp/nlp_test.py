import typing

from .nlp import *


def test_def_chars():
    def_chars()


def test_def_words():
    def_words()


def test_def_word_array():
    assert isinstance(def_word_array(), typing.Callable)
