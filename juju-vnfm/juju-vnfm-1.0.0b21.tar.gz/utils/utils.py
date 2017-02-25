#!/usr/bin/env python

#
# Project:  juju-vnfm
# file:     utils
# created:  17/02/2017 
#

"""
description goes here
"""
import logging
import sys

import os
from vnfm.sdk.exceptions import PyVnfmSdkException

__author__ = "lto"
__maintainer__ = "lto"

log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm.%s' % __name__)


def get_version():
    return '1.0.0b21'


class JujuVnfmException(PyVnfmSdkException):
    pass


def raise_juju_exception(msg):
    raise JujuVnfmException(msg)


def determine_path(root):
    try:
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        log.error("I'm sorry, but something is wrong. There is no __file__ variable. Please contact the author.")
        sys.exit(1)
