#!/usr/bin/env python

from pyplink import PyPlink

with PyPlink("input") as gen:
    for i in gen:
        break
