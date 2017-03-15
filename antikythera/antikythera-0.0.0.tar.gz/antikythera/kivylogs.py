#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" kivylogs.py

Fix Kivy's logger so it is compatible with modules
using the standard python logger, this must remain
in the same order and be at the top of the entry
point module for the application.

This code is extremely fragile and must be declared
and executed in this exact order.

"""
TRACE = 9
def trace(self, message, *args, **kws):
    """ Define trace logging level

    Yes, logger takes its '*args' as 'args'.

    """
    self._log(TRACE, message, args, **kws) 

# Add logging level TRACE
import logging
logging.addLevelName(TRACE, "TRACE") 

# Set kivy logger as root logger
from kivy.logger import Logger
logging.Logger.manager.root = Logger

# Set Logger.trace to the trace function
# This must be set up -exactly- the same as
# in the Kivy logging module or it will not work
# partial() call returns Logger.log function
# with loggin.TRACE as baked in parameter
from functools import partial
logging.Logger.trace = partial(Logger.log, logging.TRACE) 
