from gettext import bindtextdomain, textdomain, gettext, ngettext
import os
from locale import setlocale, LC_ALL
from datetime import datetime
from tzlocal import get_localzone
_domain = 'messages'
_localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
bindtextdomain(_domain, _localedir)
textdomain(_domain)
_ = gettext


def translate_created_at(created_at):
    locale = setlocale(LC_ALL)
    fmt = '%a %b %d %H:%M:%S %z %Y'
    setlocale(LC_ALL, 'C')
    created_at = datetime.strptime(created_at, fmt)
    setlocale(LC_ALL, locale)
    tz = get_localzone()
    created_at = created_at.astimezone(tz)
    return created_at.strftime('%c')


def __translate_standard_messages():
    """Argparse strings"""
    _('usage: ')
    _('argument %(argument_name)s: %(message)s')
    _(".__call__() not defined")
    _("unknown parser %(parser_name)r (choices: %(choices)s)")
    _("argument \"-\" with mode %r")
    _('%(prog)s: error: %(message)s\n')
    _("can't open '%s': %s")
    _("cannot merge actions - two groups are named %r")
    _("'required' is an invalid argument for positionals")
    _("invalid option string %(option)r: must start with a character %(prefix_chars)r")
    _("dest= is required for options like %r")
    _("invalid conflict_resolution value: %r")
    _("mutually exclusive arguments must be optional")
    _("positional arguments")
    _("optional arguments")
    _("show this help message and exit")
    _("cannot have multiple subparser arguments")
    _("unrecognized arguments: %s")
    _("not allowed with argument %s")
    _("ignored explicit argument %r")
    _("the following arguments are required: %s")
    _("one of the arguments %s is required")
    _("expected one argument")
    ngettext('expected %s argument', 'expected %s arguments', 42)
    _("expected at most one argument")
    _("expected at least one argument")
    _("ambiguous option: %(option)s could match %(matches)s")
    _("unexpected option string: %s")
    _("%r is not callable")
    _("invalid %(type)s value: %(value)r")
    _("invalid choice: %(value)r (choose from %(choices)s)")
