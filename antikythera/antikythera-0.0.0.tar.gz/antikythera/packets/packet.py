#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Packet base class.

Todo:
    * Implement location.

"""

# Standard Library
import logging

from time import time
from datetime import datetime

# Local


__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class Packet(object):
    """ Initialization of attributes common to all packets.

    Attributes:
        unix_time (float): packet creation time in seconds since UNIX epoch.
        timestamp (str): packet creation time human readable format.
        location: location packet was received.

    """
    def __init__(self):
        self.unix_time = time()
        self.timestamp = datetime.utcnow()
        self.location = "location stub"
