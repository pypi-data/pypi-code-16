#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Colin
# Date: 2017-02-10
# Desc: 自定义公用函数
#

import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])

