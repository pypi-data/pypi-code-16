"""
Package version and version utility routines
"""

########################################################################
# imports
########################################################################
# standard library imports


# standard library imports


########################################################################
# Atributes
########################################################################
__author__ = "Alan Staniforth <devops@erehwon.xyz>"
__copyright__ = "Copyright (c) 2004-2010 Alan Staniforth"
__license__ = "New-style BSD"
# Set the module version here in VERSION_INFO
# same format as sys.version_info: "A tuple containing the five components of
# the version number: major, minor, micro, releaselevel, and serial. All
# values except releaselevel are integers; the release level is 'alpha',
# 'beta', 'candidate', or 'final'. The version_info value corresponding to the
# Python version 2.0 is (2, 0, 0, 'final', 0)."  Additionally we use a
# releaselevel of 'dev' for unreleased under-development code.
VERSION_INFO = (0, 1, 0, 'dev', 1)
# for this file only we have to set __version__ manually. All other files
# should set it with a version.get_module_version_str() call
__version__ = '0.1.0a1'


########################################################################
# Interface
########################################################################
__all__ = [
            # Classes
            # Functions
            'get_version_str', 'get_package_version_str',\
            'get_package_version_info'
            ]


########################################################################
# Classes
########################################################################


########################################################################
# Functions
########################################################################


def get_version_str(in_version_info, strict=True):
    """
    Converts a version info tuple into a string.

    By default the function returns a distutils strict version string.
    In that case if the 'release level' is 'final' this is discarded
    and in the case of 'alpha', 'beta', 'candidate' and 'dev' it is
    converted into the nearest of 'a' or 'b'.

    Params:
        in_version_info: A 3-5 item tuple following the sys.version_info
                         pattern
        strict: if False then a string that can be compared with
                distutils.version.LooseVersion() will be returned.
    """
    vstring = '.'.join([
        str(in_version_info[0]),
        str(in_version_info[1]),
        str(in_version_info[2])
        ])
    if in_version_info[3] != "":
        if strict:
            if in_version_info[3] in ['alpha', 'dev']:
                vstring = "".join([vstring, 'a', str(in_version_info[4])])
            if in_version_info[3] in ['beta', 'candidate']:
                vstring = "".join([vstring, 'b', str(in_version_info[4])])
        else:
            vstring = "".join([vstring, in_version_info[3],
                              str(in_version_info[4])])
    return vstring


def get_package_version_str(strict=True):
    """
    Returns the version of this module as a string
    """
    return get_version_str(VERSION_INFO, strict)


def get_package_version_info():
    """
    Returns the version of this module as a versio info tuple
    """
    return VERSION_INFO
