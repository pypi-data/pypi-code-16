"""
codewords - Simple python library to generate "code phrases" based on
provided lists of words and delimiters.
"""

from .gen import CodeWordGenerator
from .version import __version__


__all__ = ["CodeWordGenerator"]


def get_version():
    "Return the version of the library."
    return __version__

