#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2017 Kaede Hoshikawa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from typing import Mapping, MutableMapping, TypeVar, KeysView, ValuesView, \
    ItemsView, Generic, Iterator, Iterable, Tuple, Any, Optional, List, Set, \
    Union, Dict, MappingView, Reversible, AnyStr

from ._version import version, __version__

import threading
import collections
import threading
import collections.abc
import abc

__all__ = [
    "version", "__version__", "FrozenMagicDict", "MagicDict",
    "FrozenTolerantMagicDict", "TolerantMagicDict"]

_K = TypeVar("_K")

_V = TypeVar("_V")


class _Identifier:
    pass


_DEFAULT_MARK = _Identifier()


class _MagicKeysView(KeysView[_K], Generic[_K]):
    def __init__(self, map: Union["FrozenMagicDict", "MagicDict"]) -> None:
        self._map = map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[_K]:
        for key, _ in list(self._map._kv_pairs.values()):
            yield key

    def __contains__(self, key: Any) -> bool:
        return key in self._map._pair_ids.keys()

    def __eq__(self, obj: Any) -> bool:
        return list(self) == list(obj)

    def __ne__(self, obj: Any) -> bool:
        return not self.__eq__(obj)

    def __lt__(self, obj: Iterable[Any]) -> bool:
        return set(self) < set(obj)

    def __le__(self, obj: Iterable[Any]) -> bool:
        return set(self) <= set(obj)

    def __gt__(self, obj: Iterable[Any]) -> bool:
        return set(self) > set(obj)

    def __ge__(self, obj: Iterable[Any]) -> bool:
        return set(self) >= set(obj)

    def __and__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) & set(obj)

    def __or__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) | set(obj)

    def __sub__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) - set(obj)

    def __xor__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) ^ set(obj)

    def __reversed__(self) -> "_MagicKeysView[_K]":
        return reversed(self._map).keys()  # type: ignore

    def __str__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__, repr([item for item in self]))

    __repr__ = __str__


class _MagicValuesView(ValuesView[_V], Generic[_V]):
    def __init__(self, map: Union["FrozenMagicDict", "MagicDict"]) -> None:
        self._map = map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[_V]:
        for _, value in list(self._map._kv_pairs.values()):
            yield value

    def __contains__(self, value: Any) -> bool:
        for _, _value in list(self._map._kv_pairs.values()):
            if _value == value:
                return True

        else:
            return False

    def __eq__(self, obj: Any) -> bool:
        return list(self) == list(obj)

    def __ne__(self, obj: Any) -> bool:
        return not self.__eq__(obj)

    def __reversed__(self) -> "_MagicValuesView[_V]":
        return reversed(self._map).values()  # type: ignore

    def __str__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__, repr([item for item in self]))

    __repr__ = __str__


class _MagicItemsView(
        Reversible[Tuple[_K, _V]], ItemsView[_K, _V], Generic[_K, _V]):
    def __init__(self, map: Union["FrozenMagicDict", "MagicDict"]) -> None:
        self._map = map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[Tuple[_K, _V]]:
        for key, value in list(self._map._kv_pairs.values()):
            yield (key, value)

    def __contains__(self, pair: Any) -> bool:
        return pair in self._map._kv_pairs.values()

    def __eq__(self, obj: Any) -> bool:
        return list(self) == list(obj)

    def __ne__(self, obj: Any) -> bool:
        return not self.__eq__(obj)

    def __lt__(self, obj: Iterable[Any]) -> bool:
        return set(self) < set(obj)

    def __le__(self, obj: Iterable[Any]) -> bool:
        return set(self) <= set(obj)

    def __gt__(self, obj: Iterable[Any]) -> bool:
        return set(self) > set(obj)

    def __ge__(self, obj: Iterable[Any]) -> bool:
        return set(self) >= set(obj)

    def __and__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) & set(obj)

    def __or__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) | set(obj)

    def __sub__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) - set(obj)

    def __xor__(self, obj: Iterable[Any]) -> Set[Any]:
        return set(self) ^ set(obj)

    def __reversed__(self) -> "_MagicItemsView[_K, _V]":  # type: ignore
        return reversed(self._map).items()  # type: ignore

    def __str__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__, repr([item for item in self]))

    __repr__ = __str__


class FrozenMagicDict(Reversible[_K], Mapping[_K, _V], Generic[_K, _V]):
    """
    An immutable ordered, one-to-many Mapping.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._pair_ids: Dict[_K, List[_Identifier]] = {}
        self._kv_pairs: \
            "collections.OrderedDict[_Identifier, Tuple[_K, _V]]" = \
            collections.OrderedDict()

        def add_one(key: _K, value: _V) -> None:
            identifier = _Identifier()

            if key not in self.keys():
                self._pair_ids[key] = [identifier]

            else:
                self._pair_ids[key].append(identifier)

            self._kv_pairs[identifier] = (key, value)

        if len(args):
            if len(args) > 1:  # pragma: no cover
                raise TypeError(
                    ("update expected at most 1 positional argument, "
                     "got {} args.").format(len(args)))

            else:
                if isinstance(args[0], collections.abc.Mapping):
                    for k, v in args[0].items():
                        add_one(k, v)

                elif isinstance(args[0], collections.abc.Iterable):
                    for k, v in args[0]:
                        add_one(k, v)

                else:  # pragma: no cover
                    raise TypeError(
                        ("update expected a Mapping or an Iterable "
                         "as the positional argument, got {}.")
                        .format(type(args[0])))

        for k, v in kwargs.items():
            add_one(k, v)

    def __getitem__(self, key: _K) -> _V:
        identifier = self._pair_ids[key][0]
        _, value = self._kv_pairs[identifier]
        return value

    def __iter__(self) -> Iterator[_K]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._kv_pairs)

    def __contains__(self, key: Any) -> bool:
        return key in self.keys()

    def __eq__(self, obj: Any) -> bool:
        if isinstance(obj, collections.abc.Mapping):
            return self.items() == obj.items()

        if isinstance(obj, collections.abc.Iterable):
            return self.items() == obj

        return False

    def __ne__(self, obj: Any) -> bool:
        return not self.__eq__(obj)

    def __str__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__,
            repr([(key, value) for (key, value) in self.items()]))

    def __reversed__(self) -> Iterator[_K]:
        return self.__class__(reversed(list(self.items())))

    def get_first(self, key: _K, default: Optional[_V]=None) -> Optional[_V]:
        """
        Get the first item matching the key.
        If not present, return the default.
        """
        if key not in self.keys():
            return default

        return self[key]

    def get_last(self, key: _K, default: Optional[_V]=None) -> Optional[_V]:
        """
        Get the last item matching the key.
        If not present, return the default.
        """
        if key not in self.keys():
            return default

        identifier = self._pair_ids[key][-1]
        _, value = self._kv_pairs[identifier]
        return value

    def get_iter(self, key: _K) -> Iterator[_V]:
        """
        Get an iterator that iterates over all the items matching the key.
        """
        for identifier in self._pair_ids.get(key, []):
            _, value = self._kv_pairs[identifier]

            yield value

    def get_list(self, key: _K) -> List[_V]:
        """
        Get a list that contains all the items matching the key.
        """
        return list(self.get_iter(key))

    def copy(self) -> "FrozenMagicDict[_K, _V]":
        return self.__class__(self)

    def keys(self) -> _MagicKeysView[_K]:
        return _MagicKeysView(self)

    def values(self) -> _MagicValuesView[_V]:
        return _MagicValuesView(self)

    def items(self) -> _MagicItemsView[_K, _V]:
        return _MagicItemsView(self)

    get = get_first
    __repr__ = __str__


class MagicDict(
        FrozenMagicDict[_K, _V], MutableMapping[_K, _V], Generic[_K, _V]):
    """
    A mutable version of `FrozenMagicDict`.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._lock = threading.Lock()

        FrozenMagicDict.__init__(self, *args, **kwargs)

    def __getitem__(self, key: _K) -> _V:
        with self._lock:
            identifier = self._pair_ids[key][0]
            _, value = self._kv_pairs[identifier]
            return value

    def __setitem__(self, key: _K, value: _V) -> None:
        if key in self.keys():
            del self[key]

        identifier = _Identifier()

        with self._lock:
            self._pair_ids[key] = [identifier]
            self._kv_pairs[identifier] = (key, value)

    def __delitem__(self, key: _K) -> None:
        with self._lock:
            ids = self._pair_ids.pop(key)
            for identifier in ids:
                del self._kv_pairs[identifier]

    def get_last(self, key: _K, default: Optional[_V]=None) -> Optional[_V]:
        """
        This function behaves the same as the one in  `FrozenMagicDict`
        but adds additional locking to ensure thread safety.
        """
        if key not in self.keys():
            return default

        with self._lock:
            identifier = self._pair_ids[key][-1]
            _, value = self._kv_pairs[identifier]
            return value

    def get_iter(self, key: _K) -> Iterator[_V]:
        """
        This function behaves the same as the one in  `FrozenMagicDict`
        but adds additional locking to ensure thread safety.
        """
        with self._lock:
            vals = [
                self._kv_pairs[identifier][1]
                for identifier in self._pair_ids.get(key, [])]

        for val in vals:
            yield val

    def add(self, key: _K, value: _V) -> None:
        """
        Add a value corresponding to the key without removing the former one.
        """
        if key in self.keys():
            identifier = _Identifier()

            with self._lock:
                self._pair_ids[key].append(identifier)
                self._kv_pairs[identifier] = (key, value)

        else:
            self[key] = value

    def pop(
        self, key: _K,
            default: Union[_V, _Identifier]=_DEFAULT_MARK) -> _V:
        if key not in self.keys():
            if default is _DEFAULT_MARK:
                raise KeyError(key)

            else:
                return default  # type: ignore

        with self._lock:
            identifier = self._pair_ids[key].pop()

            if len(self._pair_ids[key]) == 0:
                del self._pair_ids[key]

            _, value = self._kv_pairs.pop(identifier)

            return value

    def popitem(self, last: bool=True) -> Tuple[_K, _V]:
        """
        This method behaves exactly like `collections.OrderedDict.popitem`.

        If `last` is `True` then the items will popped by LIFO, else FIFO.
        """
        with self._lock:
            identifier, pair = self._kv_pairs.popitem(last)

            key, _ = pair

            self._pair_ids[key].remove(identifier)

            if len(self._pair_ids[key]) == 0:
                del self._pair_ids[key]

            return pair

    def update(self, *args: Any, **kwargs: Any) -> None:  # Type Hints???
        if len(args):
            if len(args) > 1:  # pragma: no cover
                raise TypeError(
                    ("update expected at most 1 positional argument, "
                     "got {} args.").format(len(args)))

            elif isinstance(args[0], collections.abc.Mapping):
                    for k, v in args[0].items():
                        self.add(k, v)

            elif isinstance(args[0], collections.abc.Iterable):
                for k, v in args[0]:
                    self.add(k, v)

            else:  # pragma: no cover
                raise TypeError(
                    ("update expected a Mapping or an Iterable "
                     "as the positional argument, got {}.")
                    .format(type(args[0])))

        for k, v in kwargs.items():
            self.add(k, v)

    def clear(self) -> None:
        with self._lock:
            self._kv_pairs.clear()
            self._pair_ids.clear()

    def setdefault(self, key: _K, default: _V=None) -> _V:
        if key in self.keys():
            return self[key]

        self[key] = default  # type: ignore
        return default  # type: ignore

    @classmethod
    def fromkeys(
            Cls, keys: Iterable[_K], value: _V=None) -> "MagicDict[_K, _V]":
        magic_dict: MagicDict[_K, _V] = Cls()

        for key in keys:
            magic_dict.add(key, value)  # type: ignore

        return magic_dict

    def copy(self) -> "MagicDict[_K, _V]":
        return self.__class__(self)


class _TolerantMagicKeysView(_MagicKeysView[AnyStr], Generic[AnyStr]):
    def __contains__(self, key: Any) -> bool:
        try:
            return super().__contains__(key.lower())

        except AttributeError:  # pragma: no cover
            return False

    def __eq__(self, obj: Any) -> bool:
        if not isinstance(obj, collections.abc.Iterable):  # pragma: no cover
            return False

        try:
            lower_obj = [item.lower() for item in iter(obj)]

        except AttributeError:  # pragma: no cover
            return False

        return super().__eq__(lower_obj)

    def __lt__(self, obj: Iterable[Any]) -> bool:
        return super().__lt__([item.lower() for item in iter(obj)])

    def __le__(self, obj: Iterable[Any]) -> bool:
        return super().__le__([item.lower() for item in iter(obj)])

    def __gt__(self, obj: Iterable[Any]) -> bool:
        return super().__gt__([item.lower() for item in iter(obj)])

    def __ge__(self, obj: Iterable[Any]) -> bool:
        return super().__ge__([item.lower() for item in iter(obj)])

    def __and__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__and__([item.lower() for item in iter(obj)])

    def __or__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__or__([item.lower() for item in iter(obj)])

    def __sub__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__sub__([item.lower() for item in iter(obj)])

    def __xor__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__xor__([item.lower() for item in iter(obj)])

    def __reversed__(self) -> "_TolerantMagicKeysView[AnyStr]":
        return reversed(self._map).keys()  # type: ignore


class _TolerantMagicItemsView(
        _MagicItemsView[AnyStr, _V], Generic[AnyStr, _V]):
    def __contains__(self, pair: Any) -> bool:
        try:
            lower_pair = (pair[0].lower(), pair[1])

        except AttributeError:  # pragma: no cover
            return False

        return super().__contains__(lower_pair)

    def __eq__(self, obj: Any) -> bool:
        if not isinstance(obj, collections.abc.Iterable):  # pragma: no cover
            return False

        try:
            lower_obj = [(k.lower(), v) for k, v in iter(obj)]

        except AttributeError:  # pragma: no cover
            return False

        return super().__eq__(lower_obj)

    def __lt__(self, obj: Iterable[Any]) -> bool:
        return super().__lt__([(k.lower(), v) for k, v in iter(obj)])

    def __le__(self, obj: Iterable[Any]) -> bool:
        return super().__le__([(k.lower(), v) for k, v in iter(obj)])

    def __gt__(self, obj: Iterable[Any]) -> bool:
        return super().__gt__([(k.lower(), v) for k, v in iter(obj)])

    def __ge__(self, obj: Iterable[Any]) -> bool:
        return super().__ge__([(k.lower(), v) for k, v in iter(obj)])

    def __and__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__and__([(k.lower(), v) for k, v in iter(obj)])

    def __or__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__or__([(k.lower(), v) for k, v in iter(obj)])

    def __sub__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__sub__([(k.lower(), v) for k, v in iter(obj)])

    def __xor__(self, obj: Iterable[Any]) -> Set[Any]:
        return super().__xor__([(k.lower(), v) for k, v in iter(obj)])

    def __reversed__(  # type: ignore
            self) -> "_TolerantMagicItemsView[AnyStr, _V]":
        return reversed(self._map).items()  # type: ignore


class FrozenTolerantMagicDict(
        FrozenMagicDict[AnyStr, _V], Generic[AnyStr, _V]):
    """
    `FrozenTolerantMagicDict` has exactly the same functionality as
    `FrozenMagicDict`. However, the keys are case-insensitive.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._pair_ids: Dict[AnyStr, List[_Identifier]] = {}
        self._kv_pairs: \
            "collections.OrderedDict[_Identifier, Tuple[AnyStr, _V]]" = \
            collections.OrderedDict()

        def add_one(key: AnyStr, value: _V) -> None:
            key = key.lower()
            identifier = _Identifier()

            if key not in self.keys():
                self._pair_ids[key] = [identifier]

            else:
                self._pair_ids[key].append(identifier)

            self._kv_pairs[identifier] = (key, value)

        if len(args):
            if len(args) > 1:  # pragma: no cover
                raise TypeError(
                    ("update expected at most 1 positional argument, "
                     "got {} args.").format(len(args)))

            else:
                if isinstance(args[0], collections.abc.Mapping):
                    for k, v in args[0].items():
                        add_one(k, v)

                elif isinstance(args[0], collections.abc.Iterable):
                    for k, v in args[0]:
                        add_one(k, v)

                else:  # pragma: no cover
                    raise TypeError(
                        ("update expected a Mapping or an Iterable "
                         "as the positional argument, got {}.")
                        .format(type(args[0])))

        for k, v in kwargs.items():
            add_one(k, v)

    def __getitem__(self, key: AnyStr) -> _V:
        return super().__getitem__(key.lower())  # type: ignore

    def get_first(
            self, key: AnyStr, default: Optional[_V]=None) -> Optional[_V]:
        return super().get_first(key.lower(), default=default)  # type: ignore

    def get_last(
            self, key: AnyStr, default: Optional[_V]=None) -> Optional[_V]:
        return super().get_last(key.lower(), default=default)  # type: ignore

    def get_iter(self, key: AnyStr) -> Iterator[_V]:
        return super().get_iter(key.lower())  # type: ignore

    def copy(self) -> "FrozenTolerantMagicDict[AnyStr, _V]":
        return self.__class__(self)

    def keys(self) -> _TolerantMagicKeysView[AnyStr]:
        return _TolerantMagicKeysView(self)

    def items(self) -> _TolerantMagicItemsView[AnyStr, _V]:
        return _TolerantMagicItemsView(self)

    get = get_first


class TolerantMagicDict(  # type: ignore
    FrozenTolerantMagicDict[AnyStr, _V],
        MagicDict[AnyStr, _V], Generic[AnyStr, _V]):
    """
    `TolerantMagicDict` has exactly the same functionality as
    `MagicDict`. However, the keys are case-insensitive.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._lock = threading.Lock()

        FrozenTolerantMagicDict.__init__(self, *args, **kwargs)

    def __getitem__(self, key: AnyStr) -> _V:
        return MagicDict.__getitem__(self, key.lower())

    def __setitem__(self, key: AnyStr, value: _V) -> None:
        MagicDict.__setitem__(self, key.lower(), value)

    def __delitem__(self, key: AnyStr) -> None:
        MagicDict.__delitem__(self, key.lower())

    def get_last(
            self, key: AnyStr, default: Optional[_V]=None) -> Optional[_V]:
        return MagicDict.get_last(  # type: ignore
            self, key.lower(), default=default)

    def get_iter(self, key: AnyStr) -> Iterator[_V]:
        return MagicDict.get_iter(self, key.lower())

    def add(self, key: AnyStr, value: _V) -> None:
        MagicDict.add(self, key.lower(), value)

    def pop(
        self, key: AnyStr,
            default: Union[_V, _Identifier]=_DEFAULT_MARK) -> _V:
        return MagicDict.pop(self, key.lower(), default)

    def copy(self) -> "TolerantMagicDict[AnyStr, _V]":
        return self.__class__(self)
