#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" GSM paging packets.

"""

import sys
import logging

from antikythera.packets.packet import Packet

__copyright__ = "Finding Ray"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)

class  Page(Packet):
    """ Paging packet attributes and factory.

    """
    def __init__(self):
        super().__init__()
        self.packet_class = "Paging"

    class Factory:
        """ Paging packet factory.

        """
        @staticmethod
        def create(type, data):
            """ Create a paging packet of the given type.

            Args:
                type (str): the type of packet subclass to create.
                data: the data to construct the packet with.

            """
            if type == "Type1": return Type1(data)
            elif type == "Type2": return Type2(data)
            elif type == "Type3": return Type3(data)
            else:
                _logger.critical("Bad packet creation of type: " + type)
                sys.exit(127)

class Type1(Page):
    """ Type1 GSM Paging Packet.

    Args:
        data: the data to construct the packet with.

    The Type1 GSM Page packet is contains only a single IMSI and either
    TMSI/P-TMSI, along with some system information for the ones being
    paged.

    Attributes:
        imsi: The IMSI of the person being paged by the network.
        page_mode: The mode of paging.
        channel_needed: The channel to connect on.
        tmsi: The TMSI for the person being paged.
        ptmsi: The P-TMSI for the person being paged.

    """
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
        self.imsi = None
        self.tmsi = None
        self.ptmsi = None
        self.page_mode = None
        self.channel_needed = None
    def __str__(self):
        return "Type1 paging packet"
    def decode(self, data):
        return data

class Type2(Page):
    """ Type2 GSM Paging Packet.

    Args:
        data: the data to construct the packet with.

    The Type2 GSM Page packets contains either a pair of TMSI/P-TMSI
    to page or an IMSI, along with some system information.

    Attributes:
        page_mode: The mode of paging.
        channel_needed: The channel to connect on.
        tmsis: A list of TMSIs being paged.
        ptmsis: A list of P-TMSIs being paged.
        imsi: The IMSI of the person being paged by the network.

    """
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
        self.imsi = None
        self.tmsis = []
        self.ptmsis = []
        self.page_mode = None
        self.channel_needed = None
    def __str__(self):
        return "Type2 paging packet"
    def decode(self, data):
        return data

class Type3(Page):
    """ Type3 GSM Paging Packet.

    Args:
        data: the data to construct the packet with.

    The Type3 GSM Page packets contains four different TMSI/P-TMSI
    to page, along with some system information.

    Attributes:
        ptmsis: A list of P-TMSIs being paged by the network.
        tmsis: A list of TMSIs being paged by the network.
        page_mode: The mode of paging.
        channel_needed: The channel to connect on.

    """
    def __init__(self, data):
        super().__init__()
        self.data = self.decode(data)
        self.tmsis = []
        self.ptmsis = []
        self.page_mode = None
        self.channel_needed = None
    def __str__(self):
        return "Type3 paging packet"
    def decode(self, data):
        return data
