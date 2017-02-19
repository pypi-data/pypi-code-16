"""
    Default configuration module
"""
from django.apps import AppConfig


class MlMarkdownConfig(AppConfig):
    """
        Default configuration for ml_markdown
    """
    name = 'ml_markdown'

    tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'div', 'pre', 'code', 'ul', 'ol', 'li',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'span', 'strong', 'em', 'a', 'img', 'blockquote',
        'hr', 'sup', 'sub', 'stroke',
    ]
    """
        Tags white list
    """

    attributes = {
        'h1': ['id'],
        'h2': ['id'],
        'h3': ['id'],
        'h4': ['id'],
        'h5': ['id'],
        'h6': ['id'],
        'a': ['href'],
        'img': ['src', 'alt'],
        'div': ['class'],
        'span': ['class'],
        'sup': ['id'],
        'li': ['id'],
    }
    """
        Attributes white lists.
        It is a dict that looks like this example:
        {
            'a': ['href', 'title'],
        }
        See bleach documentation (https://bleach.readthedocs.io/en/latest/clean.html#attribute-whitelist) for details
    """

    misaka_extensions = [
        'fenced-code',
        'footnotes',
        'math',
        'tables',
    ]
    """
        Extensions for the parser.
        Must be a list of string or an integer
        See misaka documentation for details (http://misaka.61924.nl/#extensions)
    """