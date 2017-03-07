#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from time import strptime
from django.utils.timezone import utc
from dateutil.parser import parse

STRPTIME_UTC = "%Y-%m-%d %H:%M:%S"
STRFTIME = "%Y-%m-%dT%H:%M:%S%z"

class Utils(object):

    def __init__(self, params):
        '''
        Constructor
        '''
        
    @staticmethod
    def datetime_to_isoformat(date_string):
        '''
        Force a date string to be presented in iso format for the RPRM
        '''
        print "[prpp] datetime_to_isoformat %s" % date_string
        try:
            date_string = parse(date_string).isoformat()
            return date_string
        except Exception, ex:
            print ex
            print "[prpp] ERROR Format not timezoned! %s" % date_string
            try:
                date_time = strptime(date_string, STRPTIME_UTC)
                date_time.replace(tzinfo=utc)
                return date_time.isoformat()
            except:
                print "[prpp] ERROR Format not recognized %s" % date_string
                return None
        
    