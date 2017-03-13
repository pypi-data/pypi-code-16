#!/usr/bin/env python

"""
Run a fake "serial" port for testing purposes.
"""
from __future__ import print_function

import os
import pty

import serial


def main():
    master, slave = pty.openpty()
    print(master, slave)
    s_name = os.ttyname(slave)
    print("PTY is: %s" % s_name)
    ser = serial.Serial(s_name)
    # To Write to the device
    ser.write('Your text')

    pipe = os.fdopen(master)

    # To read from the device
    print(pipe.read(1000))

    input()
    pipe.close()
#    return slave

if __name__ == "__main__":
    main()
