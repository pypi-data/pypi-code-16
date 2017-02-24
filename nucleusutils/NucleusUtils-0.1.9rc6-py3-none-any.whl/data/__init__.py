from NucleusUtils.text import prepare_text


class IterClass(object):
    """
    Base list iterator
    """

    def __init__(self, data: tuple or list):
        self._iter = 0
        self._data = data

    def __iter__(self):
        """
        Get this
        :return:
        """
        return self

    def __next__(self):
        """
        Get next item
        :return:
        """
        if self._iter < len(self._data):
            self._iter += 1
            return tuple(self._data[self._iter - 1])
        raise StopIteration()

    def __contains__(self, item):
        """
        Check contains
        :param item:
        :return:
        """
        return item in self._data

    def index(self, item):
        """
        Get index of element
        :param item:
        :return:
        """
        return self._data.index(item)


class SortedDict(object):
    """
    SortedDict() -> new empty dictionary
    SortedDict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    SortedDict(iterable) -> new dictionary initialized as if via:
        d = SortedDict()
        for k, v in iterable:
            d[k] = v
    SortedDict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  SortedDict(one=1, two=2)
    """

    def __init__(self, *args, **kwargs):
        self._data = []
        for k, v in kwargs.items():
            self[k] = v

        for arg in args:
            if not hasattr(arg, '__iter__'):
                raise AttributeError('Object is not iterable')

            if self._is_sorted_dict_data(arg):
                self._data += self._fix_sorted_dict_data(arg)
            else:
                if hasattr(arg, 'items'):
                    for key, value in arg.items():
                        self[key] = value
                else:
                    raise TypeError("'{}' object has no attribute 'items'".format(type(arg).__name__))

    @staticmethod
    def _is_sorted_dict_data(data):
        if len(data) > 0:
            for obj in data:
                if not type(obj) in (tuple, list):
                    return False
            return True
        return False

    @staticmethod
    def _fix_sorted_dict_data(data):
        result = []
        for item in data:
            if len(item) >= 2:
                result.append(list(item[:2]))

        return result

    def clear(self):
        """
        D.clear() -> None.  Remove all items from D.
        :return:
        """
        self._data.clear()

    def copy(self):
        """
        D.copy() -> a shallow copy of D
        :return:
        """
        return SortedDict(self._data)

    @staticmethod
    def fromkeys(seq, value=None):
        """
        Returns a new dict with keys from iterable and values equal to value.
        :param value:
        :param seq:
        :return:
        """
        if hasattr(seq, '__iter__'):
            result = SortedDict()
            for item in seq:
                result[item] = value
            return result
        raise AttributeError('Seq is not iterable')

    def get(self, key, default=None):
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        :param key:
        :param default:
        :return:
        """
        if key in self:
            return self[key]
        return default

    def get_index(self, key):
        """
        Get index of key
        :return:
        """
        return self.keys().index(key)

    def get_by_index(self, index):
        """
        Get element by index
        :param index:
        :return:
        """
        return tuple(self._data[index])

    class SortedDictItems(IterClass):
        pass

    def items(self):
        """
        D.items() -> a set-like object providing a view on D's items
        :return:
        """
        return self.SortedDictItems(self._data)

    class SortedDictKeys(IterClass):
        pass

    def keys(self):
        """
        D.keys() -> a set-like object providing a view on D's keys
        :return:
        """
        return self.SortedDictKeys([item[0] for item in self._data])

    def pop(self, key, default=None):
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given.
        :param key:
        :param default:
        :return:
        """
        if key in self:
            result = self[key]
            del self[key]
            return result
        return default

    def popitem(self):
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if D is empty.
        :return:
        """
        if len(self):
            result = self.get_by_index(-1)
            self._data.pop(-1)
            return result
        raise KeyError('SortedDict is empty')

    def setdefault(self, key, default=None):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        :return:
        """
        return self.get(key, default)

    def update(self, other=None, **kwargs):
        """
        D.update([E, ]) -> None.  Update D from dict/iterable other.
        If other is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If other is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        :param other:
        :return:
        """
        if hasattr(other, '__iter__'):
            if hasattr(other, 'keys'):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value, *_ in other:
                    self[key] = value
        else:
            raise TypeError("'{}' object is not iterable".format(type(other).__name__))

    def soft_update_contains(self, other):
        """
        Update only contains elements.
        :param other:
        :return:
        """
        if hasattr(other, '__iter__'):
            if hasattr(other, 'keys'):
                for key in other.keys():
                    if key in self:
                        self[key] = other[key]
            else:
                for key, value, *_ in other:
                    if key in self:
                        self[key] = value

    def soft_update_new(self, other):
        """
        Insert new keys.
        :param other:
        :return:
        """
        if hasattr(other, '__iter__'):
            if hasattr(other, 'keys'):
                for key in other.keys():
                    if key not in self:
                        self[key] = other[key]
            else:
                for key, value, *_ in other:
                    if key not in self:
                        self[key] = value

    class SortedDictValues(IterClass):
        pass

    def values(self):
        """
        D.values() -> an object providing a view on D's values
        :return:
        """
        self.SortedDictValues([item[1] for item in self._data])

    def to_dict(self):
        """
        Get SortedDict as default dict
        :return:
        """
        return {k: v for k, v in self.items()}

    def sort(self, key=lambda k, v: k, reverse=False):
        """
        Sort dictionary.
        :param key:
        :param reverse:
        :return:
        """
        self._data = sorted(self.items(), key=key, reversed=reverse)
        return self

    def reverse(self):
        """
        Reverse data
        :return:
        """
        self._data = reversed(self._data)

    def shift(self, count=1):
        """
        Shift items
        :param count:
        :return:
        """
        self._data = self._data[count:] + self._data[:count]
        return self

    def inside_out(self):
        """
        Swap the keys and values
        :return:
        """
        clone = self.copy()
        self.clear()
        for key, value in clone.items():
            self[value] = key
        del clone
        return self

    def __reversed__(self):
        return SortedDict(reversed(self._data))

    def __contains__(self, key):
        """
        True if D has a key k, else False.
        :param key:
        :return:
        """
        return key in self.keys()

    def __delitem__(self, key):
        """
        Delete self[key].
        :param key:
        :return:
        """
        if key in self:
            del self._data[self.get_index(key)]
        else:
            raise KeyError(key)

    def __eq__(self, other):
        """
        Return self==value.
        :param other:
        :return:
        """
        return self.to_dict() == other

    def __getitem__(self, key):
        """
        x.__getitem__(y) <==> x[y]
        :param key:
        :return:
        """
        if key in self:
            return self._data[self.get_index(key)][0]
        raise KeyError(key)

    def __ge__(self, other):
        """
        Return self>=value.
        :param other:
        :return:
        """
        return self.to_dict() >= other

    def __gt__(self, other):
        """
        Return self>value.
        :param other:
        :return:
        """
        return self.to_dict() > other

    def __iter__(self):
        """
        Implement iter(self).
        :return:
        """
        return self.keys()

    def __len__(self):
        """
        Return len(self).
        :return:
        """
        return len(self._data)

    def __le__(self, other):
        """
        Return self<=value.
        :param other:
        :return:
        """
        return self.to_dict() <= other

    def __lt__(self, other):
        """
        Return self<value.
        :param other:
        :return:
        """
        return self.to_dict() < other

    def __ne__(self, other):
        """
        Return self!=value.
        :param other:
        :return:
        """
        return self.to_dict() != other

    def __repr__(self):
        """
        Return repr(self).
        :return:
        """
        return '<SortedDict {}>'.format(self.__str__())

    def __str__(self):
        """
        Return str(self).
        :return:
        """
        return '{{{}}}'.format(', '.join(['{}: {}'.format(prepare_text(k), prepare_text(v)) for k, v in self.items()]))

    def __setitem__(self, key, value):
        """
        Set self[key] to value.
        :param key:
        :param value:
        :return:
        """
        try:
            self._data[self.get_index(key)] = [key, value]
        except ValueError:
            self._data.append([key, value])
