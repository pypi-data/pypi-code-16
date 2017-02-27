from zope.interface import implements
from copy import deepcopy

from rapido.core.interfaces import IRecordable

from .interfaces import IRecord


class Record(object):
    implements(IRecord, IRecordable)

    def __init__(self, context, app):
        self.context = context
        self.app = app

    def get(self, name, default=None):
        """ return an item value
        """
        if name in self:
            return self[name]
        else:
            return default

    def __getitem__(self, name):
        """ return an item value
        """
        return deepcopy(self.context.attrs[name])

    def __setitem__(self, name, value):
        """ set an item value
        """
        self.context.attrs[name] = value

    def __contains__(self, name):
        """ test if item exists
        """
        return name in self.context.attrs.keys()

    def __delitem__(self, name):
        """ remove an item
        """
        if name in self.context.attrs.keys():
            del self.context.attrs[name]

    def uid(self):
        """ return internal identifier
        """
        return self.context.intid

    def __iter__(self):
        """ return all items
        """
        return iter(self.items())

    def items(self):
        """ return all items
        """
        return dict(self.context.attrs.items())
