from markupsafe import Markup

from pyml.components import FrozenChildren, FrozenAttrs
from pyml.components.mixins import HasParentMixin
from pyml.helpers import unescape, escape as _escape, safe


class Text(HasParentMixin, Markup):
    """
    Base text element node.

    It extends the Markup object with a Component-compatible API.
    """

    __slots__ = ('_parent')

    @property
    def children(self):
        return FrozenChildren(self)

    @property
    def attrs(self):
        return FrozenAttrs(self)

    @property
    def unescaped(self):
        """
        An unescaped version of string.
        """

        return unescape(self)

    classes = ()
    id = None

    def __new__(cls, data, escape=True, parent=None):
        if isinstance(data, Markup):
            return Markup.__new__(cls, data)
        elif escape:
            try:
                data = safe(data.__html__())
                return Markup.__new__(cls, data)
            except AttributeError:
                return Markup.__new__(cls, _escape(data))
        else:
            return Markup.__new__(cls, data)

    def __init__(self, data, escape=True, parent=None):
        HasParentMixin.__init__(self, parent)

    def render(self, **kwargs):
        return self.__html__()

    def json(self):
        return {'tag': 'text', 'text': str(self)}

    def copy(self, parent=None):
        return Text(self, parent=parent)