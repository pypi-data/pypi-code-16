import re

import collections

import decimal
import yaml
from mistune import markdown as _markdown

from markio.constants import PROGRAMMING_LANGUAGES_CODES
from markio.pretty_yaml import dump as _yaml_dump

COUNTRY_CODE_RE = re.compile(
    r'^\w*(?P<i18n>([a-zA-Z][a-zA-Z])((?:-|_)(:?[a-zA-Z][a-zA-Z]))?)\w*$')
PARENTHESIS_RE = re.compile(r'.*[(](.*)[)]\w*')
WHITESPACE_RE = re.compile(r'\s*')


def indent(lines, indent=4):
    """
    Indent content with the given content level or content string.
    """

    indent = ' ' * indent if isinstance(indent, int) else indent
    return '\n'.join(indent + line for line in lines.splitlines())


def unindent(data, retlevel=False):
    """
    Remove indentation from paragraph.

    If ``retlevel=True``, Return a tuple (content, level).
    """

    re = WHITESPACE_RE

    try:
        lines = data.splitlines()
    except AttributeError:
        lines = list(data)

    get_level = lambda x: re.match(x).end()
    stripped = lambda line: line[level:] if line.strip() else ''
    level = min(get_level(line) for line in lines if line.strip())
    content = '\n'.join(map(stripped, lines))

    if retlevel:
        return content, level
    else:
        return content


def strip_trailing_whitespace(text):
    """
    Remove all whitespace in the end of each line.
    """

    lines = text.splitlines()
    lines = [x.rstrip() for x in lines]
    return '\n'.join(lines)


def normalize_i18n(x):
    """
    Normalize accepted lang codes to ISO format.

    Also check if language codes are valid.
    """

    if x is None:
        return None
    return x.replace('-', '_')


def normalize_computer_language(x):
    """
    Normalize accepted computer language strings.
    """

    x = x.lower()
    return PROGRAMMING_LANGUAGES_CODES.get(x, x)


def markdown(text):
    """
    Converts markdown to HTML.
    """

    return _markdown(text)


def load_yaml(stream, loader=yaml.Loader, object_pairs=collections.OrderedDict):
    """
    Loads YAML document.
    """

    class OrderedLoader(loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def dump_yaml(data, pretty=False):
    """
    Return a YAML string dump for the given data structure.
    """

    if not pretty:
        return yaml.safe_dump(data)
    else:
        return _yaml_dump(data)


def to_decimal(x):
    """
    Convert number to decimal
    """

    return decimal.Decimal(x)
