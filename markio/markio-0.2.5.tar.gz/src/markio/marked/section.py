import collections

from markio.utils import indent, unindent


class Section(collections.Sequence):
    """
    A section in a Marked document.
    """

    def __init__(self, title, data, tags=(), key=None):
        self.title = title
        self.data = data
        self.tags = tuple(tags)
        self.key = key or title

    def __repr__(self):
        title, content, tags = self
        data = repr(title)
        if content:
            data += ', %r' % content
        if tags:
            data += ', %r' % tags
        return '%s(%s)' % (type(self).__name__, data)

    def __iter__(self):
        yield self.title
        yield self.data
        yield self.tags

    def __len__(self):
        return 3

    def __getitem__(self, idx):
        if idx in [0, -3]:
            return self.title
        elif idx in [1, -2]:
            return self.data
        elif idx in [2, -1]:
            return self.tags
        elif isinstance(idx, int):
            raise IndexError(idx)
        else:
            return (self.title, self.data)[idx]

    def __eq__(self, other):
        if isinstance(other, (tuple, int, Section)):
            return all(x == y for x, y in zip(self, other))
        return NotImplemented

    def to_json(self):
        """
        Return a JSON-compatible triple of [title, data, tags].
        """

        return [self.title, self.data, list(self.tags)]


class SectionList(collections.MutableSequence, collections.Mapping):
    """
    A list of sections.

    It implements a list and mapping interfaces.
    """

    def __init__(self, document, data=(), casefold=True):
        self._data = list(data)
        self.document = document
        self.casefold = casefold
        self._keytrans = lambda x: x.casefold() if casefold else lambda x: x

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        if isinstance(idx, (int, slice)):
            return self._data[idx]
        if isinstance(idx, tuple):
            title, *tags = idx
            tags = tuple(tags)
        else:
            title, tags = idx, None
        if tags:
            return self._get_section_by_title_and_tags(title, tags)
        else:
            return self._get_section_by_title(title)

    def __delitem__(self, idx):
        del self._data[idx]

    def __setitem__(self, idx, value):
        self._data[idx] = value

    def __eq__(self, other):
        if isinstance(other, (SectionList, list, tuple)):
            return all(x == y for (x, y) in zip(self, other))
        return NotImplemented

    def _get_section_by_title(self, title):
        title = self._keytrans(title)
        for section in self._data:
            if self._keytrans(section.title) == title:
                return section
        raise KeyError(title)

    def _get_section_by_title_and_tags(self, title, tags):
        norm = self._keytrans
        title = norm(title)
        tags = tuple(tags)
        for section in self._data:
            if norm(section.title) == title and section.tags == tags:
                return section
        raise KeyError('%s (%s)' % (title, ', '.join(tags)))

    def insert(self, idx, value):
        self._data.insert(idx, value)

    def keys(self, normalize=False):
        if normalize:
            norm = self._keytrans
            for section in self._data:
                yield norm(section.title)
        else:
            for section in self._data:
                yield section.title

    def update_section(self, section):
        """
        Update section data or append it to the end.
        """

        title = section.title
        tags = section.tags

        try:
            old_section = self._get_section_by_title_and_tags(title, tags)
            old_section.data = section.data
        except KeyError:
            self.append(section)

    def to_json(self):
        """
        Convert to a JSON-compatible list of (title, data, tags) triples.
        """

        return [x.to_json() for x in self._data]


def section_property(name, default=None, remove_indent=False):
    """
    Return a r/w property that maps to an specific named section.
    """

    def fget(self):
        try:
            data = self.sections[name].data
        except KeyError:
            return default
        else:
            if remove_indent:
                data = unindent(data)
            return data

    def fset(self, value):
        if remove_indent:
            value = indent(value, 4)
        if value == default:
            if name in self.sections:
                del self.sections
            return

        try:
            section = self.sections[name]
            section.data = value
        except KeyError:
            section = Section(name.title(), value)
            self.sections.append(section)

    return property(fget, fset)
