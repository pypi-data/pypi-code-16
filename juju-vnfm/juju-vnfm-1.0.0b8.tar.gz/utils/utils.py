#!/usr/bin/env python

#
# Project:  juju-vnfm
# file:     utils
# created:  17/02/2017 
#

"""
description goes here
"""
from vnfm.sdk.exceptions import PyVnfmSdkException

__author__ = "lto"
__maintainer__ = "lto"


def get_version():
    return '1.0.0b8'


class JujuVnfmException(PyVnfmSdkException):
    pass
