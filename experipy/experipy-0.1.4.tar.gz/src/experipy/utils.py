
class Namespace(object):
    def __init__(self, name=None, **kwargs):
        self.__dict__.update(kwargs)
        
        if name != None:
            register(name, self)

NamespaceRegistry = {}

def register(name, namespace):
    NamespaceRegistry[name] = namespace

def nsupdate(name, attr, value):
    setattr(NamespaceRegistry[name], attr, value)

__all__ = [
    "Namespace",
    "NamespaceRegistry",
    "nsupdate",
]
