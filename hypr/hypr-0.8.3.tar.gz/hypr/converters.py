# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""URL rule converters."""

import re
import uuid


class BaseConverter:
    """Base class for all converters."""

    regex = '[^/]+'
    weight = 100

    def to_python(self, value):
        """Return the value of the segment."""
        return value


class UnicodeConverter(BaseConverter):
    """Unicode converter.

    This converter is the default converter and accepts any string but only one
    path segment.  Thus the string can not include a slash. This is the default
    validator.

    Example:

        Rule('/pages/<page>'),
        Rule('/<string(length=2):lang_code>')

    Args:
        minlength (int): the minimum length of the string.  Must be greater
            or equal 1. (default: 1)
        maxlength (int): the maximum length of the string. (default: None)
        length (int): the exact length of the string. (default: None)
    """

    def __init__(self, minlength=1, maxlength=None, length=None):
        """Init the converter."""
        super().__init__()
        if length is not None:
            length = '{%d}' % int(length)
        else:
            if maxlength is None:
                maxlength = ''
            else:
                maxlength = int(maxlength)
            length = '{%s,%s}' % (int(minlength), maxlength)

        self.regex = '[^/]' + length


class AnyConverter(BaseConverter):
    """Any converter.

    Matches one of the items provided.  Items can either be Python identifiers
    or strings.

        Rule('/<any(about, help, imprint, class, "foo,bar"):page_name>')

    Args:
        items: this function accepts the possible items as positional
            arguments.
    """

    weight = 75

    def __init__(self, *items):
        """Init the converter."""
        super().__init__()
        self.regex = '(?:%s)' % '|'.join([re.escape(x) for x in items])


class PathConverter(BaseConverter):
    """Path converter.

    Like the default :class:`UnicodeConverter`, but it also matches slashes.
    This is useful for wikis and similar applications.

        Rule('/<path:wikipage>')
        Rule('/<path:wikipage>/edit')
    """

    regex = '[^/].*?'
    weight = 200


class NumberConverter(BaseConverter):
    """Baseclass for IntegerConverter and FloatConverter."""

    weight = 50

    def __init__(self, fixed_digits=0, min=None, max=None):
        """Init converter."""
        super().__init__()
        self.fixed_digits = fixed_digits
        self.min = min
        self.max = max

    def to_python(self, value):
        """Convert matched value to the rightful python type."""
        if (self.fixed_digits and len(value) != self.fixed_digits):
            raise ValueError()
        value = self.num_convert(value)
        if (self.min is not None and value < self.min) or \
           (self.max is not None and value > self.max):
            raise ValueError()
        return value


class IntegerConverter(NumberConverter):
    """Integer converter.

    This converter only accepts integer values.

        Rule('/page/<int:page>')

    Args:
        fixed_digits: the number of fixed digits in the URL.  If you set this
            to 4 for example, the application will only match if the url looks
            like /0001. The default is variable length.
        min: the minimal value.
        max: the maximal value.
    """

    regex = r'-?\d+'
    num_convert = int


class FloatConverter(NumberConverter):
    """Float converter.

    This converter only accepts floating point values.

        Rule('/probability/<float:probability>')

    Args:
        min: the minimal value.
        max: the maximal value.
    """

    regex = r'-?(\d+.)?\d+(e[-+]\d+)?'
    num_convert = float

    def __init__(self, min=None, max=None):
        """Init converter."""
        super().__init__(0, min, max)


class UUIDConverter(BaseConverter):
    """UUID converter.

    This converter accepts valid UUIDs.

        Rule('/object/<uuid:identifier>')
    """

    weight = 80

    regex = r'[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-' \
            r'[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}'

    def to_python(self, value):
        """Convert matched value to the rightful python type."""
        return uuid.UUID(value)


DEFAULT_CONVERTERS = {
    'default':          UnicodeConverter,
    'string':           UnicodeConverter,
    'any':              AnyConverter,
    'path':             PathConverter,
    'int':              IntegerConverter,
    'float':            FloatConverter,
    'uuid':             UUIDConverter,
}
