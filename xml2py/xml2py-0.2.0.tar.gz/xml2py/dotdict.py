"""
DotDict
"""
class DotDict(dict):
    """
    DotDict is a dict whose attribute access and item access
    are equivalent.  In other words dd.x == dd['x']

    On instantiation DotDict.to_dotdict is called with the dict
    described by the arguments to __init__.

    DotDict.to_dotdict(x) can be called with any object x.
    It returns an equivalent object in which every (non DotDict)
    dict within x is converted to a DotDict.

    Keys which are dict attributes or are unsuitable as attribute
    names (e.g. pop, items, 1, $x) can still be used as DotDict
    keys, however their values are only accessable using dict
    notation.
    """
    __delattr__ = dict.__delitem__
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)
        for key, value in self.items():
            self[key] = DotDict.to_dotdict(value)

    @staticmethod
    def to_dotdict(obj):
        """The given object ``obj`` is traversed recursively and each
        (non DotDict) dict found in it is converted to a DotDict.
        """
        if isinstance(obj, DotDict):
            return obj
        elif isinstance(obj, dict):
            return DotDict(obj)
        elif isinstance(obj, list):
            return [DotDict.to_dotdict(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple([DotDict.to_dotdict(v) for v in obj])
        else:
            return obj

