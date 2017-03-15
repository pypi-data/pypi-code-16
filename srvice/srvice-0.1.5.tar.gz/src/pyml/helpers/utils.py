from html import unescape

from markupsafe import Markup, escape, escape_silent

# qa: used imports
escape = escape
escape_silent = escape_silent
unescape = unescape


def safe(x):
    """
    Convert string object to a safe Markup instance.
    """

    return Markup(x)
