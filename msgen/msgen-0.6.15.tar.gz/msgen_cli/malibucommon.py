# ----------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved. 
#  Licensed under the MIT License. See License.txt in the 
#  project root for license information.  If License.txt is 
#  missing, see https://opensource.org/licenses/MIT
# ----------------------------------------------------------

""" File for common functionality """
import os
import random
import string
import sys
from calendar import timegm
from email.utils import formatdate
from time import sleep

EXIT_MESSAGE_VIEWTIME = 10

def pause_and_display(message, debug_mode=True):
    """ Pause and show a message so it can be read by a human """
    if debug_mode:
        for second in range(0, EXIT_MESSAGE_VIEWTIME):
            print message + str(EXIT_MESSAGE_VIEWTIME-second) + " second(s)."
            sleep(1)

def get_api_url_from_base(base_url):
    """ Get the full URL given a base URL """
    if base_url.endswith("/") != True:
        base_url += "/"
    base_url += "api/workflows/"
    return base_url

def get_current_path():
    """ Get the current path of the running app """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def randomword(length):
    """ Gets a random string of the given length"""
    return ''.join(random.choice(string.lowercase) for i in range(length))

def format_rfc1123(dt):
    timestamp = timegm(dt.utctimetuple())
    return formatdate(timestamp, usegmt=True)