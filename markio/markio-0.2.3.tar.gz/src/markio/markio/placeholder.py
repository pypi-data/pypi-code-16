import collections


import collections
from warnings import warn

from markio.utils import unindent

# Language classifications
BLOCK_COMMENTS = {}
LINE_COMMENTS = {}

# Block comments in C (and languages that use the same comment syntax)
C_FAMILY = [
    # C family languages
    'c', 'cpp', 'c++', 'ansi', 'gcc', 'g++', 'clang', 'clang++', 'tcc',
    'c99', 'c++11',

    # Java
    'java', 'java6', 'java7', 'java8',

    # Javascript
    'javascript', 'js',
]
BLOCK_COMMENTS.update({k: ('/**', ' * ', ' */') for k in C_FAMILY})


# Languages that use specific characters as line comment
PY_FAMILY = [
    # Python aliases and variations
    'python', 'python3', 'python2', 'python2.7', 'py', 'py3', 'py2',
    'pypy', 'jython', 'ironpython', 'brython',

    # Python-inspired languages
    'pytuga',

    # Ruby
    'ruby',
]
LINE_COMMENTS.update({k: '# ' for k in PY_FAMILY})

LATEX_FAMILY = ['tex', 'latex']
LINE_COMMENTS.update({k: '% ' for k in LATEX_FAMILY})


class Placeholder(collections.Mapping):
    """
    Represents all placeholders as a dictionary.
    """

    @property
    def default(self):
        try:
            return unindent(self._sections['placeholder'].data)
        except KeyError:
            return None

    def __init__(self, sections):
        self._sections = sections

    def __getitem__(self, key):
        if key is None:
            return self.default
        try:
            section = self._sections['placeholder', key]
        except KeyError:
            return self._default_placeholder(key)
        return unindent(section.data)

    def __iter__(self):
        for section in self._sections:
            if section.title.casefold() == 'placeholder':
                tags = section.tags
                yield tags[0].casefold() if tags else None

    def __len__(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return repr(dict(self))

    def _default_placeholder(self, lang):
        default = self.default
        if default is None:
            return None
        else:
            return comments_to_source(default, lang)


def comments_to_source(data, lang):
    if lang in BLOCK_COMMENTS:
        start, prefix, end = BLOCK_COMMENTS[lang]
        lines = [start]
        for line in data.splitlines():
            lines.append(prefix + line)
        lines.append(end)
        return '\n'.join(lines)

    elif lang in LINE_COMMENTS:
        prefix = LINE_COMMENTS[lang]
        return '\n'.join(prefix + line for line in data.splitlines())

    else:
        warn('could not determine comment format for language: %r' % lang)
        return comments_to_source(data, 'python')