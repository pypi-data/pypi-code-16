#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xdeccba34

# Compiled with Coconut version 1.2.2 [Colonel]

"""
A suite of collection classes that emulate a small subset of those in the
Scala standard library.
"""

# Coconut Header: --------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_tee, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: ------------------------------------------------------

#Copyright 2017 Eric T. Anderson
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the license.
#==============================

import sys

try:
    from typing import Callable
    from typing import Iterable
    from typing import Any
    from typing import Union
    from typing import Optional
    import typing
except ImportError:
    Callable, Any, Iterable, Union, Optional = ["Callable", "Any", "Iterable", "Union", "Optional"]

class Maybe(object):
    """ Analogous to the Scala Option class """
    __slots__ = ['_content']

    def __init__(self, value):
# type: (...) -> None
        self._content = value

    @_coconut_tco
    def __iter__(self):
# type: (...) -> Iterable
        raise _coconut_tail_call(iter, [self._content])

    def __eq__(self, other  # type: Any
    ):
# type: (...) -> bool
        return (self.__class__ == other.__class__) and self._content == other._content

    def __ne__(self, other  # type: Any
    ):
# type: (...) -> bool
        return not self.__eq__(other)

    def __repr__(self):
# type: (...) -> str
        return self.toString

    def forall(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> bool
        return self.takeWhile(test).length == self.length

    @_coconut_tco
    def foreach(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> bool
        raise _coconut_tail_call(f, self._content)

    @property
    def get(self):
# type: (...) -> Any
        return self._content

    def getOrElse(self, f  # type: Union[Callable[[], Any], Any]
    ):
# type: (...) -> Any
        return self._content or (f() if callable(f) else f)

    def getOrNone(self):
# type: (...) -> Optional[Any]
        return self._content

    @property
    def isEmpty(self):
# type: (...) -> bool
        return self._content is None

    @_coconut_tco
    def map(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "Maybe"
        raise _coconut_tail_call(Option, f(self._content))

    @_coconut_tco
    def __rshift__(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "Maybe"
        raise _coconut_tail_call(self.map, f)

    def orElse(self, f  # type: Union[Callable[[], Any], Any]
    ):
# type: (...) -> Any
        rval = self if self._content is not None else f() if callable(f) else f
        if not isinstance(rval, Maybe):
            raise TypeError("orElse() must return a Maybe")
        return rval

    @property
    def orNone(self):
# type: (...) -> Optional["Maybe"]
        return self

    @property
    @_coconut_tco
    def toList(self):
# type: (...) -> "List"
        from .containers import List as GList
        raise _coconut_tail_call(GList, source=[self._content])

class Some(Maybe):

    def __init__(self, value):
# type: (...) -> None
        super(Some, self).__init__(value)

    def filter(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> Maybe
        return self if f(self._content) else Nothing

    @_coconut_tco
    def mkString(self, sep=None):
# type: (...) -> str
        raise _coconut_tail_call(str, self._content)

    def takeWhile(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> "List"
        from .containers import List as GList
        return GList(self._content) if test(self._content) else GList()

    @property
    def toString(self):
# type: (...) -> str
        return 'Some(%s)' % str(self._content)

class NoInstantiate(object):
    def __init__(self):
# type: (...) -> None
        super(NoInstantiate, self).__init__()
    def __new__(cls, *args, **kwargs):
# type: (...) -> None
        raise Exception("Cannot instantiate Nothing")

class NothingType(type, object):

    @property
    def get(self):
# type: (...) -> None
        raise TypeError("nothing comes of Nothing")

    @property
    def isEmpty(self):
# type: (...) -> bool
        return True

    @property
    def orNone(self):
# type: (...) -> Optional[Any]
        return None

    @property
    @_coconut_tco
    def toList(self):
# type: (...) -> "List"
        from .containers import List as GList
        raise _coconut_tail_call(GList)

    @property
    def toString(self):
# type: (...) -> str
        return "Nothing"

    def __repr__(self):
# type: (...) -> str
        return self.toString
    @_coconut_tco
    def __iter__(self):
# type: (...) -> Iterable
        raise _coconut_tail_call([].__iter__)
    def __len__(self):
# type: (...) -> int
        return 0
    @_coconut_tco
    def __rshift__(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> Maybe
        raise _coconut_tail_call(self.map, f)

    @staticmethod
    def orElse(f  # type: Union[Callable[[], Any], Any]
    ):
# type: (...) -> Any
        rval = f() if callable(f) else f
        if not isinstance(rval, Maybe):
            raise TypeError("orElse() function must return an Option")
        return rval

    @staticmethod
    def getOrNone():
# type: (...) -> Optional[Any]
        return None

    @staticmethod
    def getOrElse(f  # type: Union[Callable[[], Any], Any]
    ):
        return f() if callable(f) else f

    @staticmethod
    def filter(f):
# type: (...) -> Maybe
        return Nothing

    @staticmethod
    def foreach(f):
# type: (...) -> None
        pass

    @staticmethod
    def map(f):
# type: (...) -> Maybe
        return Nothing

    @staticmethod
    def mkString(sep=None):
# type: (...) -> str
        return ""

    @staticmethod
    @_coconut_tco
    def takeWhile(test  # type: Callable[[Any], bool]
    ):
# type: (...) -> "List"
        from .containers import List as GList
        raise _coconut_tail_call(GList)

if sys.version[0] == '2':
    Nothing = NothingType('Nothing'.encode('utf-8'), (NoInstantiate,), {})
else:
    Nothing = NothingType('Nothing', (NoInstantiate,), {})


def Option(value  # type: Optional[Any]
    ):
    return Some(value) if value is not None else Nothing
