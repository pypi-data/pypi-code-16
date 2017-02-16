#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcpinfo

tcpinfo.startUp()
flows = tcpinfo.getTcpInfoList()
for flow in flows:
    print(flow)
tcpinfo.tearDown()
