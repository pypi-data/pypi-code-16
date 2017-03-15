#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Polymorphic Packet Factory

    :py:obj:`PacketFactory` allows different types of packet factories to be
    subclassed from the base class. This is desirable to make the
    definition of packets used flexible for both quickly evolving
    technologies and security counter and counter-counter measures.

    Example:
        Packet making factories can be added using the the 
        :py:meth:`PacketFactory.addFactory()` method. These are stored 
        in the :py:data:`PacketFactory.factories` dictionary as 
        ``{ id : Factory }`` pairs. Then packets themselves can 
        be created from the factory by calling
        :py:meth:`PacketFactory.createPacket()` with the parameters
        needed to build the packet for the given packet type.

            >>> from factory import PacketFactory
            >>> factory = PacketFactory
            >>> from system import System
            >>> factory.addFactory("System", System.Factory)
            >>> sys_pkt = factory.createPacket("System", "Type1", '\x42')
            >>> sys_pkt.data
            'B'

    Note:
        The ``Factory`` objects that will be added must each be imported.

"""

import logging

# Local Imports
from antikythera.packets.system import System
from antikythera.packets.page import Page 
from antikythera.packets.assign import Assign

# from antikythera import __version__

class PacketFactory:
    """ A Polymorphic Packet Factory

    A factory for creating and using packet factories.

    Attributes:
        factories (dict): a dictionary containing some identifier value as keys
            and ``Factory`` objects stored as the pair. 

    """
    factories = {}


    @staticmethod
    def addFactory(id, factory):
        """ Add an ``{identifier : Factory}`` object pair to ``factories``.

        Args:
            id (str): the identifier can be any valid key type for a python
                dictionary.
            factory (:obj:`factory`): a packet factory subclass.

        """
        PacketFactory.factories[id] = factory


    @staticmethod
    def createPacket(id, type, data):
        """ Create a packet

        Packets are created from the given identifier coresponding to a
        factory in :py:data:`factories`, that has been created with
        :py:mod:`addFactory`, using the supplied subclass type and data.

        Args:
            id (str): A dictionary key corresponding to a key in the
                :py:data:`factories` dictionary. This selects the subclassed
                factory to create the packet from.
            type (str): the selector for the type of packet the subclassed 
                factory should create. This must match a valid type for the
                factory selected.
            data: the data to construct the packet from, type is dependant
                on ``Factory``.

        Returns:
            :obj:`antikythera.packets.packet.Packet`:
                A packet object from the input data, the type depends
                on the input but will always be a subclass of 
                :obj:`antikythera.packets.packet.Packet`.

                It will be constructed with the supplied `data`
                parameter and its attributes depend on that input.

        """
        if PacketFactory.factories[id] not in PacketFactory.factories:
            PacketFactory.factories[id] = eval(id + '.Factory()')
        return PacketFactory.factories[id].create(type, data)
