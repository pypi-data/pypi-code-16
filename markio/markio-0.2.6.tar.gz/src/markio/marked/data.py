import collections

from markio.utils import markdown


class MarkdownString(collections.UserString):
    """
    A regular markdown string that has a .html() attribute that converts it to
    HTML.
    """

    def html(self):
        """
        Return a HTML representation of string.
        """

        return markdown(str(self))


class CasefoldDict(collections.Mapping):
    """
    Dictionary with case-insensitive keys.
    """

    def __init__(self, data=None):
        self._data = dict(data or {})

    def __iter__(self):
        return iter(self._data)

    def __setitem__(self, key, value):
        self._data[self._casefold(key)] = value

    def __getitem__(self, key):
        return self._data[self._casefold(key)]

    def __len__(self):
        return len(self._data)

    def _casefold(self, key):
        try:
            return (key.casefold(),)
        except AttributeError:
            return tuple(x.casefold() for x in key)