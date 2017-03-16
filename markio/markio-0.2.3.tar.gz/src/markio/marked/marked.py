import collections
import copy

from markio.marked import Meta, Section, SectionList
from markio.utils import indent, dump_yaml


class Marked(collections.Sequence):
    """
    Represents generic *Marked* data.
    """

    def __init__(self, title='', meta=None, short_description='',
                 sections=None, parent=None):
        self.title = title
        self.meta = Meta(self, meta or {})
        self.short_description = short_description
        self.sections = SectionList(self, sections or [])
        self.parent = parent

    def __len__(self):
        return 4

    def __iter__(self):
        yield self.title
        yield self.meta
        yield self.short_description
        yield self.sections

    def __getitem__(self, idx):
        return list(self)[idx]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.title)

    def __eq__(self, other):
        if other.__class__ != self.__class__:
            return NotImplemented
        return (
            self.title == other.title and
            self.short_description == other.short_description and
            self.meta.to_json() == other.meta.to_json() and
            self.sections.to_json() == other.sections.to_json()
        )

    def source(self):
        """
        Renders generic Marked source.
        """

        # Add title
        lines = [self.title, '=' * len(self.title), '']

        # Add meta
        if self.meta:
            lines.append(indent(str(self.meta), 4))
            lines.append('')

        # Add short description
        if self.short_description:
            lines.append(str(self.short_description))
            lines.append('')

        for title, data, tags in self.sections:
            title = str(title)
            if tags:
                title = '%s (%s)' % (title, ', '.join(map(str, tags)))
            lines.extend(['', title, '-' * len(title), '', str(data), ''])

        return '\n'.join(lines)

    def pprint(self, file=None):
        """
        Pretty print Marked structure.

        See pformat() if you want the corresponding string representation.
        """

        print(self.pformat(), file=file)

    def pformat(self):
        """
        Return a pretty-print representation of the marked structure.
        """

        return dump_yaml(self.to_json(), pretty=True)

    def to_json(self):
        """
        JSON-like expansion of the Marked AST.

        All linear node instances are expanded into dictionaries.
        """

        json = collections.OrderedDict({
            'title': self.title,
        })
        if self.short_description:
            json['short_description'] = self.short_description
        if self.meta:
            json['meta'] = self.meta.to_json()
        if self.sections:
            json['sections'] = self.sections.to_json()

        return json

    def copy(self):
        """
        Return a deep copy of itself.
        """

        return copy.deepcopy(self)

    def load_title(self, title):
        """
        Computes the title attribute from a title string.
        """

        self.title = title

    def load_meta(self, meta):
        """
        Load meta information from a string of metadata.
        """

        self.meta = Meta(self, meta)

    def load_short_description(self, value):
        """
        Computes the short_description attribute from a string.
        """

        self.short_description = value

    def load_section(self, title, content, tags):
        """
        Load a section from sections and contents.
        """

        section = Section(title, content, tags)
        self.sections.update_section(section)
        return section

    def validate(self):
        """
        Can be overriden by subclasses to implement validation.
        """
