import collections

# Hierarchical Dictionary
class HierarchicalDict(collections.MutableMapping): 
    def __init__(self, *args, **kwargs): 
        self._dict = dict(*args, **kwargs)

    def __len__(self): 
        return len(self._dict)

    def __iter__(self): 
        return iter(self._dict)

    def __getitem__(self, key): 
        if not isinstance(key, str): 
            raise KeyError("{} is not a filepath-like string.")
        if '/' not in key: 
            return self._dict[key]
        else: 
            folder, _key = key.split('/',1)

            return self._dict[folder][_key]


    def __setitem__(self, key, value): 
        if not isinstance(key, str): 
            raise KeyError("{} is not a filepath-like string.")

        if '/' not in key: 
            self._dict[key] = value
        else: 
            folder, _key = key.split('/',1)

            if folder not in self._dict: 
                self._dict[folder] = HierarchicalDict()

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
        return { k : v.as_dict() if isinstance(v, HierarchicalDict) 
                 else v for k,v in self._dict.items()}

class OrderedHierarchicalDict(HierarchicalDict):
    def __init__(self, *args, **kwargs): 
        self._dict = collections.OrderedDict(*args, **kwargs)

    def as_dict(self):
        return collections.OrderedDict([
                (k, v.as_dict()) if isinstance(v, HierarchicalDict) 
                 else (k,v) for k,v in self._dict.items()])
