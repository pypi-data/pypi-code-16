#!/usr/bin/env python
'''
Utility functions for isoprene_pumpjack

Utilities have no dependencies, and should not interdepend.
'''

import logging

from flask_restful import Resource


def object_fullname(obj):
    '''Returns the full absolute name of the object provided'''
    fullname = obj.__module__ + "." + obj.__class__.__name__
    return fullname

def object_logger(obj):
    '''Returns a correctly named logger for the given object'''
    fullname = object_fullname(obj)
    logger = logging.getLogger(fullname)
    return logger

class SmartResource(Resource):
    '''Smart resource that initiates logging on creation'''
    def __init__(self):
        self.logger = object_logger(self)

