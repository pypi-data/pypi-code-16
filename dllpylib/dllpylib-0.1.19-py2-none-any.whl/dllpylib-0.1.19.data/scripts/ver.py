#!python

""" Helper utility to maintain package's 'VERSION.
    Reads "major.minor.build" from a given file and conditionaly (see parser below) updates these numbers.
    Updated numbers are stored in the given file.
    Displays final version.
"""

import sys

from optparse import OptionParser


def get_opts_and_args():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default="ver.txt")
    parser.add_option("-m", "--incr-minor", dest="incr_minor", action='store_true', default=False)
    parser.add_option("-M", "--incr-major", dest="incr_major", action='store_true', default=False)
    parser.add_option("-b", "--incr-build", dest="incr_build", action='store_true', default=False)
    parser.add_option("-0", "-z", "--zero-all", dest="zero", action='store_true', default=False)
    return parser.parse_args()


if __name__ == "__main__":
    opts, args = get_opts_and_args()
    try:
        with open(opts.filename, "rt") as f:
            line = f.readline()
        major, minor, build = [int(i) for i in line.split(".")]
    except Exception as e:
        """ Be carefull no warning will be issued or insert print statement below """
        major = 0
        minor = 0
        build = 0
    if opts.zero:
        major = 0
        minor = 0
        build = 0
    if opts.incr_major:
        major += 1
        minor = 0
        build = 0
    if opts.incr_minor:
        minor += 1
        build = 0
    if opts.incr_build:
        build += 1
    ver = "%d.%d.%d" % (major, minor, build)
    with open(opts.filename, "wt") as f:
        f.write("%s\n" % ver)
    print(("%s" % ver))
    sys.exit(0)
