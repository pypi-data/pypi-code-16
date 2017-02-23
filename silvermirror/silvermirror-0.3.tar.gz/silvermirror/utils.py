#!/usr/bin/env python

import netifaces
import os
import sys


def home():
    # XXX needed? better way of doing?
    return os.environ['HOME']


def ip_addresses():
    """dictionary of ip4 addresses for the machine"""
    interfaces = []
    for i in netifaces.interfaces():
        try:
            value = netifaces.ifaddresses(i).get(2)
            if value:
                interfaces.append(i)
        except ValueError:
            continue

    return dict([(i, netifaces.ifaddresses(i)[2][0]['addr'])
                 for i in interfaces
                 ])


def main(args=sys.argv[1:]):
    for name, value in sorted(ip_addresses().items()):
        print ('%s : %s' % (name, value))


if __name__ == '__main__':
    main()
