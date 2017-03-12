from collections import defaultdict
from inspect import isclass

from fito.operations import Operation


class Query(object):
    def __init__(self, **kwargs):
        self.dict = kwargs

    def set(self, key, val):
        if isclass(val): val = val.__name__
        self.dict[key] = val
        return self

    def matches(self, operation):
        return self._matches(self.todict(), operation.to_dict())

    def _matches(self, query_dict, op_dict):
        for k, v1 in query_dict.iteritems():

            if k not in op_dict: return False
            v2 = op_dict[k]
            if isinstance(v2, dict) != isinstance(v1, dict): return False
            if isinstance(v2, dict) and isinstance(v1, dict):
                return self._matches(v1, v2)
            elif v1 != v2:
                return False
        return True

    def todict(self):
        res = infinitedict()
        for key, val in self.dict.iteritems():
            d = res
            subkeys = key.split('.')
            for subkey in subkeys[:-1]:
                d = d[subkey]

            key = subkeys[-1]
            if isclass(val) and issubclass(val, Operation):
                d[key]['type'] = val.__name__
            else:
                d[key] = val

        return res.todict()


class infinitedict(defaultdict):
    def __init__(self):
        super(infinitedict, self).__init__(infinitedict)

    def todict(self):
        res = {}
        for k, v in self.iteritems():
            if isinstance(v, infinitedict):
                res[k] = v.todict()
            else:
                res[k] = v
        return res
