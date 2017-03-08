#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd86f4540

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


import functools
import itertools
if _coconut_sys.version_info < (3, 3):
    import collections as abc
else:
    import collections.abc as abc
try:
    from typing import Any
    from typing import Dict
    from typing import Callable
    from typing import Iterable
    from typing import Tuple
    import typing
except ImportError:
    Any, Dict, Callable, Iterable, Tuple = ["Any", "Dict", "Callable", "Iterable", "Tuple"]

from .option import Some
from .option import Nothing
from .option import Maybe

def reify(f  # type: Callable
    ):
# type: (...) -> Callable
    """
    A decorator to call the BaseCollection_reify method before invoking the wrapped method.
    Reification is needed prior to calling methods that work on fully-realized collection elements
    rather than iterator or generator sources.  Example: BaseCollection.length()
    """
    @functools.wraps(f)
    @_coconut_tco
    def wrapped(self, *args, **kwargs):
        self._reify()
        raise _coconut_tail_call(f, self, *args, **kwargs)
    return wrapped

class BaseCollection(abc.Sequence):
    __slots__ = ['_content', '_source']

    def __init__(self, value  # type: Any
    ):
# type: (...) -> None
        """
        Generic initializer for a collection instance.
        :param value: native (python) collection or None
        :type value: object
        :return: None
        :rtype: None
        """
        super(BaseCollection, self).__init__()
        assert value is not None
        self._source, self._content = value, None

    def _reify(self):
# type: (...) -> None
        raise NotImplementedError

    @reify
    def __call__(self, index  # type: int
    ):
# type: (...) -> Any
        """Returns the item at the specified index in the collection.
        :param index: index in collection to fetch from
        :type index
        :return: The object at the specified index
        :rtype: object
        """
        if index > (self.length - 1):
            raise IndexError("index %i out of bounds" % index)
        return self._content[index]

    @_coconut_tco
    def __getitem__(self, index):
        raise _coconut_tail_call(self.__call__, index)

    @_coconut_tco
    def __contains__(self, what  # type: Any
    ):
# type: (...) -> bool
        """ Support Pythonic 'x in collection' expressions """
        raise _coconut_tail_call(self.contains, what)

    @reify
    def __eq__(self, other  # type: Any
    ):
        return type(self) is type(other) and other._equals(self)

    @reify
    @_coconut_tco
    def __hash__(self):
# type: (...) -> int
        raise _coconut_tail_call(self._content.__hash__)

    @reify
    @_coconut_tco
    def __iter__(self):
# type: (...) -> typing.Iterator
        raise _coconut_tail_call(iter, self._content.items() if isinstance(self._content, dict) else [] if self.isEmpty else self._content)

    @_coconut_tco
    def __rshift__(self, f  # type: Callable
    ):
# type: (...) -> "BaseCollection"
        """ override >> operator, make it a synonym for the map method """
        raise _coconut_tail_call(self.map, f)

    @reify
    def _equals(self, other  # type: Any
    ):
# type: (...) -> bool
        return other._content == self._content

    @reify
    def contains(self, other  # type: Any
    ):
# type: (...) -> bool
        return other in self._content

    @reify
    @_coconut_tco
    def count(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> int
        def _count(thing  # type: Any
    ):
            _coconut_match_check = False
            _coconut_match_to = thing
            if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) >= 1):
                tail = _coconut.list(_coconut_match_to[1:])
                head = _coconut_match_to[0]
                _coconut_match_check = True
            if _coconut_match_check:
                return (0, 1)[f(head)] + _count(tail)
            if not _coconut_match_check:
                _coconut_match_to = thing
                if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) == 0):
                    _coconut_match_check = True
                if _coconut_match_check:
                    return 0
            if not _coconut_match_check:
                raise TypeError()
        raise _coconut_tail_call(_count, list(self._content))

    def filter(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> Any
        raise NotImplementedError
        return None

# '>=' alias for map()
    @_coconut_tco
    def __ge__(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> bool
        raise _coconut_tail_call(self.filter, f)

#def __and__(self, other) = self.filter(other)

    @reify
    @_coconut_tco
    def find(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> Maybe
        def _find(thing  # type: Any
    ):
# type: (...) -> Maybe
            _coconut_match_check = False
            _coconut_match_to = thing
            if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) >= 1):
                tail = _coconut.list(_coconut_match_to[1:])
                head = _coconut_match_to[0]
                _coconut_match_check = True
            if _coconut_match_check:
                return Some(head) if f(head) is True else _find(tail)
            if not _coconut_match_check:
                _coconut_match_to = thing
                if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) == 0):
                    _coconut_match_check = True
                if _coconut_match_check:
                    return Nothing
            if not _coconut_match_check:
                raise TypeError()

        raise _coconut_tail_call(_find, list(self._content))

    @reify
    @_coconut_tco
    def fold(self, init,  # type: Any
     f  # type: Callable[[Any], Any]
    ):
# type: (...) -> Any
        if self.isEmpty:
            raise TypeError("fold() called on empty container")
        raise _coconut_tail_call((_coconut_partial(reduce, {0: f, 2: init}, 3)), self)

    @reify
    def forall(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> bool
        return len(list(itertools.takewhile(test, self))) == self.length

    @reify
    def foreach(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> None
        (consume)((_coconut.functools.partial(map, f))(self._content))

    @property
    @reify
    def isEmpty(self):
# type: (...) -> bool
        return self._content is None or len(self._content) == 0

    @property
    @reify
    @_coconut_tco
    def length(self):
# type: (...) -> int
        raise _coconut_tail_call(len, self._content)

    def __len__(self):
# type: (...) -> int
        return self.length

    def map(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "BaseCollection"
        raise NotImplementedError

    def mkString(self, separator=""  # type: str
    ):
# type: (...) -> str
        if self._content is not None:
            st = separator.join((_coconut.functools.partial(map, lambda _=None: str(_)))(self._content))
        else:
            st = "source=" + str(self._source)
        return st

    @reify
    @_coconut_tco
    def reduce(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> Any
        if self.isEmpty:
            raise TypeError("reduce() called on empty container")
        raise _coconut_tail_call((_coconut.functools.partial(reduce, f)), self._content)

    @property
    def size(self):
# type: (...) -> int
        return self.length

    def takeWhile(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> "BaseCollection"
        raise NotImplementedError

    @_coconut_tco
    def _zip(self, cls,  # type: object
     other  # type: Iterable[Any]
    ):
# type: (...) -> "BaseCollection"
        raise _coconut_tail_call(cls, source=zip(self, other))

    @_coconut_tco
    def _zipWithIndex(self, cls  # type: object
    ):
# type: (...) -> "BaseCollection"
        raise _coconut_tail_call(cls, source=zip(self._content.items() if isinstance(self._content, dict) else self._content, range(0, self.length)))

    @_coconut_tco
    def _tail(self, cls  # type: object
    ):
# type: (...) -> "BaseCollection"
        if self.isEmpty:
            raise IndexError("tail() called on empty collection")
        raise _coconut_tail_call(cls, source=list(self._content)[1:])

    def _head(self, cls  # type: object
    ):
# type: (...) -> Any
        if self.isEmpty:
            raise IndexError("head() called on empty collection")
        return list(self._content)[0]

class List(BaseCollection):

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(kwargs['source'] if 'source' in kwargs else args)
        if not 'source' in kwargs:
            self._reify()

    @reify
    @_coconut_tco
    def __add__(self, other  # type: "List"
    ):
# type: (...) -> "List"
        other._reify()  #TODO add external property to get at reified contents of other
        raise _coconut_tail_call(List, source=self._content + other._content)

    def _reify(self):
# type: (...) -> None
        if self._content is None:
            self._content = tuple(self._source)
            self._source = None

    def __repr__(self):
# type: (...) -> str
        return self.toString

    @_coconut_tco
    def filter(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> "List"
        src = self._content if self._content is not None else self._source  # type: Iterable[Any]
        raise _coconut_tail_call(List, source=(_coconut.functools.partial(filter, f))(src))

    @property
    @reify
    @_coconut_tco
    def flatten(self):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=itertools.chain.from_iterable(self._content))

    def flatMap(self, f):
# type: (...) -> "List"
        return self.map(f).flatten

    @property
    @reify
    @_coconut_tco
    def head(self):
# type: (...) -> Any
        raise _coconut_tail_call(self._head, List)

    @reify
    @_coconut_tco
    def indexOf(self, what,  # type: Any
     index=0  # type: int
    ):
# type: (...) -> int
        raise _coconut_tail_call(self.indexWhere, lambda _=None: _ == what, index)

    @reify
    def indexWhere(self, test,  # type: Callable[[Any], bool]
     index=0  # type: int
    ):
# type: (...) -> int
        rval = -1
        if index >= 0 and index < (len(self._content) - 1):
            for (i, x) in enumerate(self._content[index:]):
                if test(x) is True:
                    rval = i + index
                    break
        return rval

    @property
    @reify
    def last(self):
# type: (...) -> Any
        if self.length == 0:
            raise IndexError("last() called on empty List")
        return self._content[-1]

    @property
    @reify
    @_coconut_tco
    def list(self):
# type: (...) -> typing.List
        raise _coconut_tail_call(list, self._content)

    @_coconut_tco
    def map(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=(_coconut.functools.partial(map, f))((self._content or self._source)))

    @property
    @reify
    @_coconut_tco
    def reverse(self):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=list(self._content).reverse())

    @property
    @reify
    @_coconut_tco
    def sorted(self):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=sorted(self._content))

    @reify
    @_coconut_tco
    def sortedWith(self, key):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=sorted(self._content, key=key))

    @property
    @reify
    @_coconut_tco
    def sum(self):
# type: (...) -> Any
        raise _coconut_tail_call(sum, self._content)

    @property
    @reify
    @_coconut_tco
    def tail(self):
# type: (...) -> Any
        raise _coconut_tail_call(self._tail, List)

    @reify
    def take(self, count  # type: int
    ):
# type: (...) -> "List"
        return (List() if count <= 0 or self.length == 0 else List(source=self._content) if count >= self.length else List(source=self._content[:count]))

    @reify
    def takeRight(self, count  # type: int
    ):
# type: (...) -> "List"
        return (List() if count < 1 or self.length == 0 else List(source=self._content) if count >= self.length else List(source=self._content[count:]))

    @reify
    def takeWhile(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> "List"
        return (List() if self.length == 0 else List(source=itertools.takewhile(test, self._content)))

    @property
    @_coconut_tco
    def toList(self):
# type: (...) -> "List"
        raise _coconut_tail_call(List, source=self.list)

    @property
    @_coconut_tco
    def toSet(self):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=(s for s in self.list))

    @property
    def toString(self):
# type: (...) -> str
        return 'List(%s)' % self.mkString(", ")

    @reify
    @_coconut_tco
    def zip(self, other):
# type: (...) -> "List[Tuple[Any]]"
        raise _coconut_tail_call(self._zip, List, other)

    @reify
    @_coconut_tco
    def zipWithIndex(self):
# type: (...) -> "List[Tuple[int, Any]]"
        raise _coconut_tail_call(self._zipWithIndex, List)

class Map(BaseCollection):

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(kwargs['source'] if 'source' in kwargs else args)
        if not 'source' in kwargs:
            self._reify()
        else:
            if isinstance(self._source, (type({}), type([]),)):
                self._reify()

    def __repr__(self):
# type: (...) -> str
        return self.toString

    @reify
    def __call__(self, key  # type: Any
    ):
# type: (...) -> Any
        return self._content[key]

    def _reify(self):
# type: (...) -> None
        if self._content is None:
            self._content = dict(self._source)
            self._source = None

    @reify
    def contains(self, key  # type: Any
    ):
# type: (...) -> bool
        return key in self._content

    @reify
    @_coconut_tco
    def count(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> int
        def ft(*_coconut_match_to_args, **_coconut_match_to_kwargs):
            _coconut_match_check = False
            if (_coconut.len(_coconut_match_to_args) == 2) and ("acc" not in _coconut_match_to_kwargs) and (_coconut.isinstance(_coconut_match_to_args[1], _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to_args[1]) == 2):
                _coconut_match_temp_0 = _coconut_match_to_args[0] if _coconut.len(_coconut_match_to_args) > 0 else _coconut_match_to_kwargs.pop("acc")
                k = _coconut_match_to_args[1][0]
                v = _coconut_match_to_args[1][1]
                if (not _coconut_match_to_kwargs):
                    acc = _coconut_match_temp_0
                    _coconut_match_check = True
            if not _coconut_match_check:
                _coconut_match_err = _coconut_MatchError("pattern-matching failed for " "'def ft(acc,(k,v)) = acc + (0,1)[f(k,v)]'" " in " + _coconut.repr(_coconut.repr(_coconut_match_to_args)))
                _coconut_match_err.pattern = 'def ft(acc,(k,v)) = acc + (0,1)[f(k,v)]'
                _coconut_match_err.value = _coconut_match_to_args
                raise _coconut_match_err

            return acc + (0, 1)[f(k, v)]
        raise _coconut_tail_call((_coconut_partial(reduce, {0: ft, 2: 0}, 3)), self._content.items())

    @reify
    @_coconut_tco
    def filter(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> "Map"
        raise _coconut_tail_call(Map, source=dict(((k, v) for k, v in self._content.items() if f(k, v))))

    @reify
    @_coconut_tco
    def find(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> Maybe
        for k, v, in self._content.items():
            if f(k, v):
                raise _coconut_tail_call(Some, (k, v))
        return Nothing

    @reify
    @_coconut_tco
    def forall(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> bool
        def _forall(seq  # type: Iterable
    ):
# type: (...) -> bool
            _coconut_match_check = False
            _coconut_match_to = seq
            if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) >= 1):
                tail = _coconut.list(_coconut_match_to[1:])
                head = _coconut_match_to[0]
                _coconut_match_check = True
            if _coconut_match_check:
                k, v = head
                return False if not test(k, v) else _forall(tail)
            if not _coconut_match_check:
                _coconut_match_to = seq
                if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) == 0):
                    _coconut_match_check = True
                if _coconut_match_check:
                    return True
        raise _coconut_tail_call(_forall, list(self._content.items()))

    @reify
    def get(self, key  # type: Any
    ):
# type: (...) -> Maybe
        return Nothing if not key in self._content else Some(self._content[key])

    @reify
    def getOrElse(self, key,  # type: Any
     default  # type: Any
    ):
        return self._content[key] if key in self._content else default

    @property
    @reify
    def head(self):
# type: (...) -> Tuple[Any, Any]
        if self.length == 0:
            raise IndexError("head() called on empty Map")
        h = list(self._content.items())[0]
        return (h[0], h[1])

    @property
    @reify
    @_coconut_tco
    def tail(self):
# type: (...) -> "Map"
        if self.isEmpty:
            raise IndexError("tail() called on empty collection")
        raise _coconut_tail_call(Map, source=list(self._content.items()[1:]))

    @reify
    @_coconut_tco
    def isDefinedAt(self, key  # type: Any
    ):
# type: (...) -> bool
        raise _coconut_tail_call(self.contains, key)

    @property
    @reify
    def last(self):
# type: (...) -> Tuple[Any, Any]
        keys = list(self._content.keys())
        if not keys:
            raise IndexError("last() called on empty Map")
        key = keys[-1]
        return (key, self._content[key])

    @_coconut_tco
    def map(self, f):
# type: (...) -> "Map"
        items = self._content.items() if self._content is not None else self._source
        raise _coconut_tail_call(Map, source=(f(k, v) for (k, v) in items))

    def mkString(self, separator=""  # type: str
    ):
# type: (...) -> str
        return separator.join((_coconut.functools.partial(map, lambda _=None: (str)(_)))(self._content.items())) if self._content is not None else str(self._source)

    @reify
    @_coconut_tco
    def takeWhile(self, test  # type: Callable[[Any], bool]
    ):
# type: (...) -> "Map"
        @_coconut_tco
        def _take(acc,  # type: Dict
     thing  # type: Iterable
    ):
            while True:
                _coconut_match_check = False
                _coconut_match_to = thing
                if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) >= 1):
                    tail = _coconut.list(_coconut_match_to[1:])
                    head = _coconut_match_to[0]
                    _coconut_match_check = True
                if _coconut_match_check:
                    k, v = head
                    if test(k, v):
                        acc[k] = v
                        if _take is _coconut_recursive_func_79:
                            acc, thing = acc, tail
                            continue
                        else:
                            raise _coconut_tail_call(_take, acc, tail)

                    else:
                        return acc
                if not _coconut_match_check:
                    _coconut_match_to = thing
                    if (_coconut.isinstance(_coconut_match_to, _coconut.abc.Sequence)) and (_coconut.len(_coconut_match_to) == 0):
                        _coconut_match_check = True
                    if _coconut_match_check:
                        return acc
                return None
        _coconut_recursive_func_79 = _take
        raise _coconut_tail_call(Map, source=_take({}, list(self._content.items())))

    @property
    @reify
    @_coconut_tco
    def dict(self):
# type: (...) -> Dict
        raise _coconut_tail_call(dict, self._content)

    @property
    @reify
    @_coconut_tco
    def toList(self):
# type: (...) -> List
        raise _coconut_tail_call(List, source=self._content.items())

    @property
    @reify
    @_coconut_tco
    def toSet(self):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=(item for item in self._content.items()))

    @property
    def toString(self):
# type: (...) -> str
        return 'Map(%s)' % (self.mkString(", "))

    @_coconut_tco
    def zip(self, other):
# type: (...) -> Tuple[Any, Any]
        raise _coconut_tail_call(self._zip, Map, other)

    @property
    @_coconut_tco
    def zipWithIndex(self):
# type: (...) -> Tuple[int, Any]
        raise _coconut_tail_call(self._zipWithIndex, Map)

class Set(BaseCollection):

    def __init__(self, *args, **kwargs):
# type: (...) -> None
        super(Set, self).__init__(kwargs['source'] if 'source' in kwargs else args)
        if not 'source' in kwargs:
            self._reify()
#super(Set, self).__init__(kwargs['source'] if 'source' in kwargs else set(args))

    @reify
    def __call__(self, value  # type: Any
    ):
# type: (...) -> bool
        return value in self._content

    def __repr__(self):
# type: (...) -> str
        return self.toString

    def _reify(self):
# type: (...) -> None
        if self._content is None:
            self._content = frozenset((s for s in self._source))
            self._source = None

    @property
    @reify
    def content(self):
# type: (...) -> Iterable
        return self._content

    @_coconut_tco
    def filter(self, f  # type: Callable[[Any], bool]
    ):
# type: (...) -> "Set"
        src = self._content if self._content is not None else self._source
        raise _coconut_tail_call(Set, source=(_coconut.functools.partial(filter, f))(src))

    @property
    @reify
    @_coconut_tco
    def flatten(self):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=itertools.chain.from_iterable(self._content))

    @reify
    def flatMap(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "Set"
        return self.map(f).flatten

    @property
    @reify
    @_coconut_tco
    def head(self):
# type: (...) -> Any
        raise _coconut_tail_call(self._head, Set)

    @reify
    @_coconut_tco
    def intersect(self, other  # type: "Set"
    ):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=self._content.intersection(other.content))

    @property
    @reify
    def last(self):
# type: (...) -> Any
        if self.length == 0:
            raise IndexError("last() called on empty Set")
        return list(self._content)[-1]

    @_coconut_tco
    def map(self, f  # type: Callable[[Any], Any]
    ):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=(_coconut.functools.partial(map, f))((self._content or self._source)))

    @property
    @reify
    @_coconut_tco
    def set(self):
# type: (...) -> set
        raise _coconut_tail_call(set, self._content)

    @property
    @reify
    @_coconut_tco
    def sum(self):
# type: (...) -> Any
        raise _coconut_tail_call(sum, self._content)

    @property
    @reify
    @_coconut_tco
    def tail(self):
# type: (...) -> "Set"
        raise _coconut_tail_call(self._tail, Set)

    @reify
    @_coconut_tco
    def takeWhile(self, test  # type: Callable[[Any], Any]
    ):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=(_coconut.functools.partial(takewhile, test))(self._content))

    @property
    @reify
    @_coconut_tco
    def toList(self):
# type: (...) -> List
        raise _coconut_tail_call(List, source=self._content)

    @property
    def toString(self):
# type: (...) -> str
        return 'Set(%s)' % self.mkString(", ")

    @reify
    @_coconut_tco
    def union(self, other):
# type: (...) -> "Set"
        raise _coconut_tail_call(Set, source=self._content.union(other.set))

    @reify
    @_coconut_tco
    def zip(self, other):
# type: (...) -> "Set[Tuple[Any,Any]]"
        raise _coconut_tail_call(self._zip, Set, other)

    @property
    @reify
    @_coconut_tco
    def zipWithIndex(self):
# type: (...) -> "Set[Tuple[int, Any]]"
        raise _coconut_tail_call(self._zipWithIndex, Set)
