#!/usr/bin/env python

'''
Windows starter program for EPICS Qt motor demo
'''

import sys
import motor_qt

if __name__ == '__main__':
    sys.argv.append('xxx:m1')
    motor_qt.main()
