import six
from .mapper import MappedClass
from .graphObject import GraphObject


class TypeDataObject(six.with_metaclass(MappedClass, GraphObject)):
    def __init__(self, ident):
        super(TypeDataObject, self).__init__()
        self.ident = ident
        self.defined = True

    def identifier(self):
        return self.ident

    def __hash__(self):
        return hash(self.ident)
