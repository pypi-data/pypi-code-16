# compat2.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


###
# Function
###
def _readlines(fname):  # pragma: no cover
    """ Read all lines from file """
    with open(fname, 'r') as fobj:
        return fobj.readlines()
