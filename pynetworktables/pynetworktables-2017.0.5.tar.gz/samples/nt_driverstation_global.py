#!/usr/bin/env python3
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

try:
    table = NetworkTables.getGlobalTable()
    
    i = 0
    while True:
        try:
            print('robotTime:', table.getNumber('/SmartDashboard/robotTime'))
        except KeyError:
            print('robotTime: N/A')
    
        table.putNumber('/SmartDashboard/dsTime', i)
        time.sleep(1)
        i += 1
    
finally:
    NetworkTables.shutdown()    
