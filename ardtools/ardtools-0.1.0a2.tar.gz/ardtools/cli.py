# -*- coding: utf-8 -*-
"""
Holds 'console_scripts' entry points for package
"""


########################################################################
# Package/Module imports
########################################################################
# standard library imports
import argparse
from argparse import ArgumentParser


# package specific imports
from version import get_package_version_str
from .tools import restart_screen_sharing
from .util import CommandAction, switch


########################################################################
# Atributes
########################################################################
__author__ = "Alan Staniforth <devops@erehwon.xyz>"
__copyright__ = "Copyright (c) 2004-2016 Alan Staniforth"
__license__ = "New-style BSD"
__version__ = get_package_version_str()


########################################################################
# Interface
########################################################################
__all__ = [
            # Classes
            'main_tool'
            ]


########################################################################
# Constants
########################################################################
ARDTOOLS_COMMANDS = ['r', 'restart']
COMMAND_HELP_TEXT = \
    """
    Command you want ardtools to execute. Accepted commands are:

    'r' or 'restart' - restart the ARD service and its helper agent;
    """


########################################################################
# Classes
########################################################################


########################################################################
# Functions
########################################################################

def main_tool():
    # parse options and args
    parser = ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="ARDTools")

    parser.add_argument('-v', '--version', action='version',
                        version="%(prog)s ("+__version__+")")

    parser.add_argument(
        "command", metavar='COMMAND', type=str, nargs=1,
        choices=ARDTOOLS_COMMANDS, action=CommandAction,
        help=COMMAND_HELP_TEXT)

    args = parser.parse_args()

    for case in switch(args.command):
        if case('r') or case('restart'):
            restart_screen_sharing()
            break
