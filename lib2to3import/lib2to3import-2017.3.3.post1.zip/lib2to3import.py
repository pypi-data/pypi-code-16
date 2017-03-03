"""""\
lib2to3import
===============

lib2to3import is a utility to apply Python 2 to 3 code translation on import.

w/o lib2to3import
-------------------

  >>> from py2codes import py2_print
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "py2codes/py2_print.py", line 1
      print "Written when Python 2 was majority."
                                                ^
  SyntaxError: Missing parentheses in call to 'print'

With lib2to3import
--------------------

  >>> from lib2to3import import lib2to3importer, prepending
  >>> fixers = ["lib2to3.fixes.fix_print"]
  >>> with prepending(lib2to3importer(fixers, "py2codes.")):
  ...     from py2codes import py2_print
  ...
  Written when Python 2 was majority.

Limitation
------------

There's no way to apply fixes to 2 different roots concurrently.

When you apply fixes to both 'foo.module' and 'bar.module' at one time, you
have to leave out prefix parameter, that makes fixes applied to all of modules
and packages to be imported.

**Concurrent import**::

  from lib2to3import import lib2to3importer, prepending
  fixers = ["lib2to3.fixes.fix_print"]

  with prepending(lib2to3importer(fixers)):
      import foo.module  #  import chain: 1. foo.module -> 2. bar.module

**2 steps import (Recommended)**::

  from lib2to3import import lib2to3importer, prepending
  fixers = ["lib2to3.fixes.fix_print"]

  with prepending(lib2to3importer(fixers, "bar.")):
      import bar.module  # ... 2

  with prepending(lib2to3importer(fixers, "foo.")):
      import foo.module  # ... 1
"""

from contextlib import contextmanager
from importlib.machinery import FileFinder
from importlib.machinery import SOURCE_SUFFIXES
from importlib.machinery import SourceFileLoader
from itertools import chain
from lib2to3.refactor import RefactoringTool
import os
import sys
from zipimport import zipimporter

import chardet


VERSION = (2017, 3, 3)
VERSION_TEXT = ".".join(map(str, VERSION)) + ".post1"

__version__ = VERSION_TEXT
__license__ = "MIT"
__author__ = "Youhei Sakurai"
__email__ = "sakurai.youhei@gmail.com"
__all__ = ["lib2to3importer", "lib2to3zipimporter", "prepending"]

_CACHE_TAG = sys.implementation.cache_tag


class Lib2to3Loader(object):
    """Generic class to realize on-the-fly translation."""
    def __init__(self, *args, fixers, prefix):
        super().__init__(*args)
        self._fixers = fixers
        self._prefix = prefix or ""

    @classmethod
    def apply(cls, fixers, prefix):
        def apply_for_Lib2to3Loader(*args):
            return cls(*args, fixers=fixers, prefix=prefix)
        return apply_for_Lib2to3Loader

    def refactor(self, source):
        return RefactoringTool(self._fixers).refactor_string(
            source, " ".join(chain([__name__], self._fixers)))

    def get_code(self, fullname):
        """Proxy method that may disable code cache temporarily."""
        # Preserve last value
        cache_tag = sys.implementation.cache_tag
        if fullname.startswith(self._prefix):
            # Ensure no use of .pyc
            sys.implementation.cache_tag = None
        else:
            # Ensure default behavior
            sys.implementation.cache_tag = _CACHE_TAG
        try:
            return super().get_code(fullname)
        finally:
            # Restore last value
            sys.implementation.cache_tag = cache_tag

    def get_data(self, path):
        """Proxy method that may translate source code on load."""
        data = super().get_data(path)
        if not os.path.splitext(path)[1] in SOURCE_SUFFIXES:
            return data  # Only .py can be translated
        elif not self.name.startswith(self._prefix):
            return data  # Out of translation scope
        else:
            encoding = chardet.detect(
                data).get("encoding") or sys.getdefaultencoding()
            source = data.decode(encoding, errors="ignore")
            return str(self.refactor(source)).encode(encoding, errors="ignore")


class Lib2to3FileLoader(Lib2to3Loader, SourceFileLoader):
    pass


class Lib2to3ZipImporter(Lib2to3Loader, zipimporter):
    pass


def lib2to3importer(fixers, prefix=None):
    """Returns finder closure to be prepended to sys.path_hooks.

    :param fixers: e.g. ["lib2to3.fixes.fix_exec", "lib2to3.fixes.fix_long"]
    :param prefix: Prefix of module or package name to apply fixes.
        Unless provided, fixes are applied to all of modules and packages.
    """
    loader = Lib2to3FileLoader.apply(fixers, prefix)
    return FileFinder.path_hook((loader, SOURCE_SUFFIXES))


def lib2to3zipimporter(fixers, prefix=None):
    """Returns importer closure to be prepended to sys.path_hooks.

    :param fixers: e.g. ["lib2to3.fixes.fix_exec", "lib2to3.fixes.fix_long"]
    :param prefix: Prefix of module or package name to apply fixes.
        Unless provided, fixes are applied to all of modules and packages.
    """
    return Lib2to3ZipImporter.apply(fixers, prefix)


@contextmanager
def prepending(importer):
    path_hooks = sys.path_hooks
    sys.path_hooks = sys.path_hooks.copy()
    sys.path_hooks.insert(0, importer)
    sys.path_importer_cache.clear()
    try:
        yield importer
    finally:
        sys.path_hooks = path_hooks
