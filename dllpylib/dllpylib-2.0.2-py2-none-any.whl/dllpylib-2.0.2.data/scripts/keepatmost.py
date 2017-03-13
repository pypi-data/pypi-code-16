#!python
# -*- coding: utf-8 -*-

from   optparse import OptionParser
import os
from dllpylib import retain_most_recently_used

"""
    RETMRC - Retain Most Recently Created

    usage: retmrc.py [-o count ] [--only=count] [filename [filename ... ] ]

    Ensure only 'count' files exist and they are most recently created.

    In other words, for each pattern if count of files matching that pattern is greater than 'count',

    delete least recently created files to leave only 'count'

"""
DESCR = "Retain Most Recently Created (files), i.e. delete oldest files and leave not more than 'count'"
USAGE = "Usage: %prog [options] [file_name1 [file_name2 ...]]"
VER = "1.0.0"
def get_options():
    parser = OptionParser(usage=USAGE, version=VER,description=DESCR)
    parser.add_option("-c", "--count", dest="count", type=int, help="Number of files to retain", default=3)
    parser.add_option("--doit", dest="doit", action="store_true", default=False, help="Do removal. Otherwise don't")
    parser.add_option("-q", "--quiet",
                      action="store_true",
                      dest="quiet",
                      default=False,
                      help="Don't print status messages to stdout")
    (options, args) = parser.parse_args()
    return (options,args)

if __name__ == "__main__":
    options, args = get_options()
    retain_most_recently_used(options.count, args[1:], quiet=options.quiet, delete=options.doit)
