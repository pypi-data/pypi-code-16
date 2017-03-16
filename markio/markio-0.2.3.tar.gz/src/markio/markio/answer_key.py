import collections

from markio.marked import Section
from markio.utils import unindent, indent


class AnswerKey(collections.Mapping):
    """
    Represents all answer keys as a dictionary.
    """

    def __init__(self, sections):
        self._sections = sections

    def __getitem__(self, key):
        section = self._sections['answer key', key]
        return unindent(section.data)

    def __setitem__(self, key, source):
        source = indent(source, 4)
        try:
            section = self._sections['answer key', key]
            section.data = source
        except KeyError:
            section = Section('Answer Key', source, (key,))
            self._sections.append(section)

    def __iter__(self):
        for section in self._sections:
            if section.title.casefold() == 'answer key':
                yield section.tags[0].casefold()

    def __len__(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return repr(dict(self))

    def add(self, source, language):
        """
        Add/replace answer key for the given language
        """

        self[language] = source
