#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2017-02-16 14:27:57
# Filename      : __init__.py
# Description   : 

from __future__ import print_function, unicode_literals
from .lock import IPLocker
import tempfile
import os.path

__ALL__ = ["locked", "IP", "lock", "unlock"]

LK_PATH = os.path.join(tempfile.gettempdir(), "iplock/")

_locker = IPLocker(LK_PATH)
lock = _locker.lock
unlock = _locker.unlock

IP = _locker.get

