#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from antikythera.packets.factory import PacketFactory
from antikythera.packets.system import System
from antikythera.packets.page import Page
from antikythera.packets.assign import Assign

__author__ = "Derek Goddeau"
__copyright__ = "Derek Goddeau"
__license__ = "gpl3"

@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """ This fixture will be run code before and after every test.

    Reset the global class variable ``factories`` after each test.

    """
    # Code that will run before test
    factory = PacketFactory
    factory.factories = {}

    # A test function will be run at this point
    yield

    # Code that will run after test
    pass

#####################
#                   #
# Test addFactory() #
#                   #
#####################

def test_addFactory_none():
    factory = PacketFactory
    assert factory.factories == {}

def test_addFactory_system_factory():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    assert factory.factories == {"System" : System.Factory}

def test_addFactory_page_factory():
    factory = PacketFactory
    factory.addFactory("Page", Page.Factory)
    assert factory.factories == {"Page" : Page.Factory}

def test_addFactory_assign_factory():
    factory = PacketFactory
    factory.addFactory("Assign", Assign.Factory)
    assert factory.factories == {"Assign" : Assign.Factory}

#######################
#                     #
# Test createPacket() #
#                     #
#######################

# Test system packets

def test_createPacket_system_packet_type1():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type1", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type2():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type2", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type3():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type3", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type4():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type4", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type2ter():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type2ter", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type2quarter():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type2quarter", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_system_packet_type13():
    factory = PacketFactory
    factory.addFactory("System", System.Factory)
    sys_pkt = factory.createPacket("System", "Type13", '\x42')
    assert sys_pkt.data == 'B'


# Test page packets

def test_createPacket_page_packet_type1():
    factory = PacketFactory
    factory.addFactory("Page", Page.Factory)
    sys_pkt = factory.createPacket("Page", "Type1", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_page_packet_type2():
    factory = PacketFactory
    factory.addFactory("Page", Page.Factory)
    sys_pkt = factory.createPacket("Page", "Type2", '\x42')
    assert sys_pkt.data == 'B'

def test_createPacket_page_packet_type3():
    factory = PacketFactory
    factory.addFactory("Page", Page.Factory)
    sys_pkt = factory.createPacket("Page", "Type3", '\x42')
    assert sys_pkt.data == 'B'

# Test assign packets

def test_createPacket_assign_packet_immediate():
    factory = PacketFactory
    factory.addFactory("Assign", Assign.Factory)
    sys_pkt = factory.createPacket("Assign", "Immediate", '\x42')
    assert sys_pkt.data == 'B'
