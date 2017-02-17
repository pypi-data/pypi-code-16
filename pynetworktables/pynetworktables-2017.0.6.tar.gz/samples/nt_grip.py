#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This is a NetworkTables client (eg, the DriverStation/coprocessor side).
# You need to tell it the IP address of the NetworkTables server (the
# robot or simulator).
#
# When running, this will continue incrementing the value 'dsTime', and the
# value should be visible to other networktables clients and the robot.
#

import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]

NetworkTables.initialize(server=ip)

sd = NetworkTables.getTable("/GRIP/myContoursReport")
#sna.append(1)

#sd.putValue('centerX', na)
sd.putStringArray('sau', (u'𐄜', '2017'))

i = 0

while True:
    try:
        pass
        #print('centerX:', ret)
    except KeyError:
        print('centerX: N/A')

    time.sleep(1)
    i += 1

