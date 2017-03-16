import re
import sys

from markio.errors import MarkioSyntaxError
from markio.marked.marked import Marked
from markio.utils import unindent


def parse_marked(src, **kwargs):
    """
    Parse a Marked source code and return the parsed AST.

    Args:
        src (str or file):
            Marked source code.

    This function assumes the document has the following structure:

        Title
        =====

            # An indented YAML source with meta information
            meta1: value
            meta2: value

        Short description paragraph.

        Or maybe two paragraphs ;-)


        Subsection 1
        ------------

        Subsection data. We won't complain if you use invalid markdown source
        here.


        Subsection 2
        ------------

        You can use how many sections you like.

    The resulting :class:`Marked` object is a linear structure with ``title``,
    ``meta``, ``short_description``, and ``sections`` attributes. The later is
    basically a sequence of (title, data) pairs.
    """

    parser = MarkedParser(src, **kwargs)
    return parser.parse()


class MarkedParser:
    """
    Generic parser for Marked documents.

    Prefer to use the :func:`parse` function instead of manually instantiating
    this class.

    Sub-formats should pass a ``document_class`` callable that creates an empty
    document. It is probably necessary to override the ``.load_*()`` methods to
    control how raw data is inserted into the document.
    """

    TITLE_RE = re.compile(r'^')
    WHITESPACE_RE = re.compile(r'^\s*')
    LINE_RE = re.compile(r'-*')

    def __init__(self, source, document_class=Marked):
        self.lineno = 0
        self.source = source
        try:
            self.data = source.read()
            if isinstance(self.data, bytes):
                self.data = self.data.decode('utf8')
        except AttributeError:
            self.data = str(source)
        self.stream = list(enumerate(self.data.splitlines(), 1))
        self.stream.reverse()
        self.parsed = document_class()

    def __bool__(self):
        return bool(self.stream)

    def pop(self):
        """
        Pop next (lineno, line) on stream.

        Return None if no line is available.
        """

        try:
            pair = self.stream.pop()
            self.lineno = pair[0]
            return pair
        except ValueError:
            pass

    def push(self, *args):
        """
        Accept either .push(lineno, line) or .push(line).

        Insert line back to the stream.
        """

        if len(args) == 2:
            self.stream.append(args)
        else:
            line, = args
            self.stream.append((self.lineno, line))

    def skip_blank(self):
        """
        Skip all blank lines.
        """

        lineno, line = 0, ''
        while not line.strip():
            item = self.pop()
            if item is None:
                return
            lineno, line = item
        self.push(lineno, line)

    def read_indented(self):
        """
        Read all indented lines and return a pair of (level, content) with the
        string contents with indentation removed and the current indentation
        level.
        """

        lines = []

        # Separate lines starting with spaces
        while self:
            lineno, line = self.pop()
            if (not line) or line[0] in ' \t':
                lines.append(line)
            else:
                self.push(lineno, line)
                break

        # Return empty content
        if not lines:
            return 0, ''

        # Remove trailing empty lines
        while lines:
            if not lines[-1].strip():
                lines.pop()
            else:
                break

        # Create content string and determine indentation level
        content, level = unindent(lines, retlevel=True)
        return level, content

    def read_before_title(self, prefix):
        """
        Consumes content until a title is reached.

        Return the content string.
        """

        data = []

        re = self.LINE_RE
        while self:
            lineno, line = self.pop()
            if line.startswith(prefix):
                self.push(lineno, line)
                break
            elif re.match(line).end() == len(line) != 0:
                title = data.pop()
                self.push(lineno, line)
                self.push(lineno - 1, title)
                break
            else:
                data.append(line)

        return '\n'.join(data)

    def read_title(self, underline_char, prefix):
        """
        Read title with the using the given underline character.
        """

        self.skip_blank()
        _, title = self.pop()

        # Check if title is in the heading hash tag form
        if title.startswith(prefix):
            return title[len(prefix):].strip()

        # No hash tags: search for a underline
        lineno, underline = self.pop()

        # Strip trailing spaces
        title = title.rstrip()
        underline = underline.rstrip()

        # Check underline length
        chars = set(underline)
        if len(chars) != 1 or chars != {underline_char}:
            raise MarkioSyntaxError(
                "line %s: title should have an underline formed of '%s' "
                "characters." % (lineno, underline_char)
            )
        if len(underline) != len(title):
            raise MarkioSyntaxError(
                'line %s: expect a underline of %s characters.' %
                (lineno, len(title))
            )
        return title.lstrip()

    def parse(self):
        """
        Return a Marked object with document's parse tree.
        """

        self.parse_title()
        self.parse_meta()
        self.parse_short_description()
        self.parse_sections()
        return self.parsed

    def parse_title(self):
        title = self.read_title('=', '# ')
        self.parsed.load_title(title)

    def parse_meta(self):
        self.skip_blank()
        _, content = self.read_indented()
        meta = content
        self.parsed.load_meta(meta)

    def parse_short_description(self):
        short_description = self.read_before_title('## ').rstrip()
        self.parsed.load_short_description(short_description)

    def parse_sections(self):
        while self:
            self.parse_section()

    def parse_section(self):
        title = self.read_title('-', '## ')
        content = self.read_before_title('## ').rstrip()
        content = content.strip('\r\n')
        title, tags = split_tags(title)
        title = title.rstrip()
        self.parsed.load_section(title, content, tags)


def split_tags(title):
    """
    Split the title part from the corresponding tags.
    """

    title = title.rstrip()
    if not title.endswith(')'):
        return title, []

    title, _, tags = title.rpartition('(')
    tags = tags[:-1].split(',')
    tags = [x.strip() for x in tags]
    return title, tags
