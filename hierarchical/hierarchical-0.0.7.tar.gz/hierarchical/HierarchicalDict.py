import abc
import collections

# Hierarchical Dictionary
class HierarchicalMapping(collections.MutableMapping, metaclass=abc.ABCMeta): 
    @abc.abstractproperty
    def _base_dict(self): pass

    @classmethod
    def _new_dict(cls):
        return cls()

    def __init__(self, *args, **kwargs): 
        self._dict = self._base_dict(*args, **kwargs)

    def __len__(self): 
        return sum(v.size() if isinstance (v, HierarchicalMapping)
                   else 1 for v in self.values())

    def __iter__(self): 
        for k, v in self._dict.items():
            if isinstance(v, HierarchicalMapping):
                for k0 in iter(v):
                    yield k+'/'+k0
            else:
                yield k

    def __getitem__(self, key): 
        if not isinstance(key, str): 
            raise KeyError("{} is not a filepath-like string.")
        if '/' not in key: 
            return self._dict[key]
        else: 
            folder, _key = key.split('/',1)
            if _key == '': 
                return self._dict[folder]
            else: 
                return self._dict[folder][_key]


    def __setitem__(self, key, value): 
        if not isinstance(key, str): 
            raise KeyError("{} is not a filepath-like string.")

        if '/' not in key: 
            self._dict[key] = value
        else: 
            folder, _key = key.split('/',1)

            if folder not in self._dict: 
                self._dict[folder] = self._new_dict()

            self._dict[folder][_key] = value
        

    def __delitem__(self, key): 
        if not isinstance(key, str): 
            raise KeyError("{} is not a filepath-like string.")
        if '/' not in key: 
            del self._dict[key]
        else: 
            folder, _key = key.split('/',1)

            del self._dict[folder][_key]

    def __str__(self): 
        return str(self.as_dict())

    def as_dict(self):
        return self._base_dict([(k, v.as_dict()) if isinstance(v, HierarchicalMapping) 
                 else (k,v) for k,v in self._dict.items()])

    def is_dir(self, key): 
        try: 
            val = self.__getitem__(key)
            return isinstance(val, HierarchicalMapping)
        except KeyError: 
            return False

class HierarchicalDict(HierarchicalMapping):
    _base_dict = dict

class OrderedHierarchicalDict(HierarchicalDict):
    _base_dict = collections.OrderedDict
