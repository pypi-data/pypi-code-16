#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GSM immediate assignment packets.

"""

import sys
import logging

from antikythera.packets.packet import Packet

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class  Assign(Packet):
    """ Immediate assignment packet attributes and factory.

    """
    def __init__(self):
        super().__init__()
        self.packet_class = "Immediate Assignment"

    class Factory:
        """ Immediate assignment packet factory.

        """
        @staticmethod
        def create(type, data):
            """ Create an immediate assignment packet of the given type.

            Args:
                type (str): the type of packet subclass to create.
                data: the data to construct the packet with.

            """
            if type == "Immediate": return Immediate(data)
            else:
                _logger.critical("Bad packet creation of type: " + type)
                sys.exit(127)

class Immediate(Assign):
    """ GSM Immediate Assignment Packet.

    Args:
        data: the data to construct the packet with.

    Attributes:
        time_slot: When to connect.
        page_mode: Extended Paging.

    """
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
        self.time_slot = None
        self.page_mode = None
    def __str__(self):
        return "Immediate assignment packet"
    def decode(self, data):
        return data
