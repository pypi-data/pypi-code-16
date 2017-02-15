"""This package provides a very simple function to register a handler for all signals that could be captured.

.. moduleauthor:: Tim Kittel <Tim.Kittel@pik-potsdam.de>

"""

from ._simple_signal_handler import register_signals, NUMBER_TO_SIGNAL, ALL_SIGNALS

def versioninfo2version(v_info):
    return ".".join(map(str, v_info))


__version_info__ = version_info = (0, 1)  # that's where it all started
"""version as a tuple in the format (major, minor)"""

__version__ = version = versioninfo2version(version_info)
"""version as a str in the format 'major.minor'"""





