#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcpinfo

values = tcpinfo.getListOfAvailableValues()

print(str(len(values)) + " available values:")
print(values)
