# -*- coding: utf-8 -*-
"""
Tools to control screen sharing from the command line
"""


########################################################################
# Package/Module imports
########################################################################
# standard library imports


# package specific imports
from version import get_package_version_str
from util import exec_cli


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
            'restart_screen_sharing'
            ]


########################################################################
# Constants
########################################################################
RESTART_CMD_LIST = ["sudo", "/System/Library/CoreServices/RemoteManagement/"
                    "ARDAgent.app/Contents/Resources/kickstart", "-restart",
                    "-agent"]

ACTIVATE_CMD_LIST = ["sudo", "/System/Library/CoreServices/RemoteManagement/"
                     "ARDAgent.app/Contents/Resources/kickstart", "-activate"]


########################################################################
# Classes
########################################################################


########################################################################
# Functions
########################################################################

def restart_screen_sharing():
    """
    Stops and restarts the ARD and its helper agent.

    Seems to be necessary to issue an 'activate' as well as the 'restart' to
    wake up the screen sharing on a headless Mac restarted without a monitor
    connected.

    Adapted from the advice found at <https://support.apple.com/en-gb/HT201710>
    """
    print "Restarting ARD..."
    restart_out = exec_cli(RESTART_CMD_LIST, False, echo=True)
    print "Activating ARD..."
    activate_out = exec_cli(ACTIVATE_CMD_LIST, False, echo=True)
