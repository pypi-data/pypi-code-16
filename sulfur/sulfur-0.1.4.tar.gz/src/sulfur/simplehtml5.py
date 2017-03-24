import collections
import re

from sulfur.errors import ValidationError

# Generic regex
spaces_re = re.compile(r'\s+')

# Opening tag processors
tag_separator_re = re.compile(r'(?:\s*/>|\s*>|\s+)')
opt_spaces_re = re.compile(r'\s*')
tagname_re = re.compile(r'\w([-a-zA-Z]*\w+)?')

# Attribute names
attr_name_re = re.compile(r'(\w|_)([-a-zA-Z_]*(\w|_)+)?')
eq_sign_re = re.compile(r'\s*=\s*')
string_re = re.compile(r'"[^"]*"')
attr_value_re = re.compile(r'(\w|_)([-a-zA-Z_]*(\w|_)+)?')

# CLosing tags
self_closing_tags = {'br', 'link', 'meta'}
CLOSE_TAG = object()


class ValidatingMixin:
    """
    Implement the create_valid() and validate() methods.
    """

    @classmethod
    def create_valid(cls, *args, **kwargs):
        """
        Create a new instance and immediately validate it.

        Arguments are passed to the constructor.
        """

        instance = cls(*args, **kwargs)
        instance.validate()
        return instance

    def validate(self):
        """
        Validate element.

        Raises an ValidationError() if validation fails.
        """

        raise NotImplementedError


class HtmlElement(ValidatingMixin):
    """
    Base HTML class for Tags/Document and other HTML elements.
    """

    tag = None
    self_closing = False

    def __init__(self, children=None):
        self.children = list(children or [])

    def add(self, tag):
        """
        Add a new child element to itself.
        """

        if isinstance(tag, Text) and tag.isspace() or tag is None:
            return
        self.children.append(tag)

    def render(self):
        """
        Renders HTML structure as string.
        """

        return ''.join(c.render() for c in self.children)


class Document(HtmlElement):
    """
    Root node for the HTML AST.
    """

    def __repr__(self):
        return '<html>'


class HtmlTag(HtmlElement):
    """
    Represents a generic HTML tag.
    """

    @property
    def self_closing(self):
        """
        If True, means that the tag is self-closing (e.g. <br>).
        """

        return self.tag in self_closing_tags

    def __init__(self, tag, children=None, attributes=None):
        super().__init__(children)
        self.tag = tag
        self.attributes = list(attributes or [])

    def __repr__(self):
        return '<%s>' % self.tag

    def validate(self):
        validate_tag_name(self.tag)

    def render_attributes(self):
        """
        Render the attributes part of string.
        """

        if not self.attributes:
            return ''
        else:
            data = []
            for name, value in self.attributes:
                if value is None:
                    data.append(' %s' % name)
                else:
                    data.append(' %s=%s' % (name, value))
            return ''.join(data)

    def render(self):
        if self.self_closing and not self.children:
            return '<%s>' % self.tag
        children = super().render()
        attr_data = self.render_attributes()
        return '<%s%s>%s</%s>' % (self.tag, attr_data, children, self.tag)


class TextBase(ValidatingMixin, collections.UserString):
    """
    Base class for HTML text fragments.
    """

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def validate(self):
        if '<' in self.data or '>' in self.data:
            raise ValidationError('forgot to escape <> inside text')

    def render(self):
        return str(self)


class DOCTYPE(TextBase):
    """
    The doctype declaration on top of the HTML source file.

    HTML5 doctype is simply this::

        <!DOCTYPE html>
    """

    def validate(self):
        if self != 'html':
            raise ValidationError('please use the <!DOCTYPE html> declaration '
                                  'for html5 documents.')

    def render(self):
        return '<!DOCTYPE %s>' % self.data


class Comment(TextBase):
    """
    Data inside HTML comments::

        <!-- This is an HTML comment -->
    """

    def validate(self):
        if '-->' in self:
            raise ValidationError('invalid comment: closing twice with "-->"')

    def render(self):
        return '<!--%s-->' % self


class Text(TextBase):
    """
    A text fragment in an HTML source.
    """

    def validate(self):
        if tagname_re.fullmatch(self.tag) is None:
            raise ValidationError('invalid tag name: %r' % self.tag)


class SimpleHtml5Validator:
    """
    Base HTML5 validator class.

    Simple API::

        validator = SimpleHtml5Validator(source)
        validator.validate()

    Users should use the validate() function. This class exists publicly to be
    subclassed.
    """

    def __init__(self, data, doctype=False, head=False, body=False,
                 encoding='utf8'):
        self.data = data
        self.doctype = doctype
        self.head = head
        self.body = body
        self._stream = self.data
        self._document = Document()
        self._open_tags = [self._document]
        self._current = self._document
        if hasattr(self._stream, 'decode'):
            self._stream = self._stream.decode(encoding)

    def _parse_comments(self):
        data, sep, self._stream = self._stream[4:].partition('-->')
        if not sep:
            raise ValidationError('expect --> to close a comment.')
        return Comment(data)

    def _parse_doctype(self):
        data, sep, self._stream = self._stream.partition('>')
        if (not sep) or (not data) or (data[9] != ' '):
            raise ValidationError('invalid doctype declaration: %s>' % data)
        data = data[10:]  # remove "<!DOCTYPE "
        return DOCTYPE.create_valid(data.strip())

    def _parse_text(self):
        data, sep, missing = self._stream.partition('<')
        self._stream = sep + missing
        return Text(data)

    def _parse_tag(self):
        tagname, sep, self._stream = re_partition(tag_separator_re,
                                                  self._stream)
        tagname += sep.strip()
        tagname = tagname[1:]
        tag_kwargs = {}
        if tagname.endswith('/>'):
            tagname = tagname[:-2]
        elif tagname.endswith('>'):
            tagname = tagname[:-1]
        else:
            tag_kwargs = self._parse_tag_attrs(tagname)
        tag = HtmlTag.create_valid(tagname.strip(), **tag_kwargs)
        self._open_tags.append(tag)
        return tag

    def _parse_tag_attrs(self, tagname):
        attributes = []
        result = {'attributes': attributes}
        while not (self._stream.startswith('>') or
                       self._stream.startswith('/>')):
            # We start reading an attribute name and then process it
            # looking for a possible value in the rhs of the equality
            name, self._stream = read_tok(attr_name_re, self._stream)
            if not name:
                msg = 'expect attribute on open "%s" tag' % tagname
                raise ValidationError(msg)

            # Now we look for the "=" sign to decide if we must check the
            # rhs of the attribute declaration
            op, self._stream = read_tok(eq_sign_re, self._stream)
            if not op:
                value = None
            elif self._stream.startswith('"'):
                value, self._stream = read_tok(string_re, self._stream)
            else:
                value, sep, self._stream = re_partition(
                    tag_separator_re, self._stream)
                if sep.strip():
                    self._stream = sep.strip() + self._stream
                if not attr_value_re.fullmatch(value):
                    msg = 'invalid tag attribute: %r' % value
                    raise ValidationError(msg)

            attributes.append((name, value))
            self._check_stream_has_not_ended(tagname=tagname)

        self._stream = self._stream[1:]  # strip the first ">" character
        return result

    def _check_stream_has_not_ended(self, tagname=None):
        if not self._stream:
            if tagname:
                msg = '">" expected for closing %s tag' % tagname
                raise ValidationError(msg)
            else:
                raise ValidationError('stream ended unexpectedly')

    def _parse_endtag(self):
        tag, _, self._stream = self._stream.partition('>')
        tagname = tag[2:]  # remove "</"
        if not tagname_re.fullmatch(tagname):
            raise ValidationError('invalid closing tag name: %s' % tagname)

        while self._open_tags:
            last = self._open_tags.pop()
            if last.tag == tagname:
                break
            elif last.self_closing:
                continue
            raise ValidationError('forgot to close tag: %r' % last.tag)
        else:
            raise ValidationError(
                'closing tag </%s> without an open tag.' % tagname
            )
        return CLOSE_TAG

    def _parse_from_re(self, regex):
        match = regex.match(self._stream)
        if match is None:
            return False

        end = match.end()
        data = self._stream[:end]
        self._stream = self._stream[end:]
        return data

    def _parse_next(self):
        data = self._stream
        if data.startswith('<!--'):
            return self._parse_comments()
        if data.startswith('<!'):
            return self._parse_doctype()
        elif data.startswith('</'):
            return self._parse_endtag()
        elif data.startswith('<'):
            return self._parse_tag()
        else:
            return self._parse_text()

    def validate(self):
        """
        Parse document and raise a ValidationError in case of an invalid
        document.
        """

        while self._stream:
            elem = self._parse_next()
            if elem is CLOSE_TAG:
                self._current = self._open_tags[-1]
            else:
                self._current.add(elem)
                if isinstance(elem, HtmlTag):
                    self._current = elem

        return self._document


def re_partition(re, st):
    match = re.search(st)
    if match is None:
        return st, '', ''
    i = match.start()
    j = match.end()
    if i == j == 0:
        return st, '', ''
    return st[:i], st[i:j], st[j:]


def read_tok(re, st):
    match = re.match(st)
    if match:
        return st[:match.end()], st[match.end():]
    else:
        return '', st


def validate_tag_name(tagname):
    """
    Raise ValidationError() if tagname is not valid.
    """

    if tagname_re.fullmatch(tagname) is None:
        raise ValidationError('invalid tag name: %r' % tagname)


def validate(html_str, **kwargs):
    """
    Validate string of HTML source.

    Args:
        html_str (str):
            A string of HTML source.
        doctype:
            If True, ensures that the document has the HTML5 doctype.
        head:
            If True, ensures that document has a <head> element. (This is *not*
            required by the HTML5 spec, but most users want to enforce that).
        body:
            If True, ensures that document has a <body> element. (This is *not*
            required by the HTML5 spec, but most users want to enforce that).

    Returns:
        An Document() instance with the document AST.
    """

    validator = SimpleHtml5Validator(html_str, **kwargs)
    return validator.validate()
