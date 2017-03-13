#!python

""" Helper utility to maintain package's 'VERSION.
    Reads "major.minor.build" from a given file and conditionaly (see parser below) updates these numbers.
    Updated numbers are stored in the given file.
    Displays final version.
"""
import re
import sys
from optparse import OptionParser

def fmt2re(s):
    rv =  s.replace("{M}", "(?P<major>[0-9]+)")
    rv =  rv.replace("{m}", "(?P<minor>[0-9]+)")
    rv =  rv.replace("{b}", "(?P<build>[0-9]+)")
    rv =  rv.replace(".", r"\.")
    return rv

def get_opts_and_args():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default=None)
    parser.add_option("-m", "--incr-minor", dest="incr_minor", action='store_true', default=False)
    parser.add_option("-M", "--incr-major", dest="incr_major", action='store_true', default=False)
    parser.add_option("-b", "--incr-build", dest="incr_build", action='store_true', default=False)
    parser.add_option("-0", "-z", "--zero-all", dest="zero", action='store_true', default=False)
    parser.add_option("-p", "--pattern", dest="pattern", default="{M}.{m}.{b}")
    return parser.parse_args()


if __name__ == "__main__":
    opts, args = get_opts_and_args()
    fmt_as_re = fmt2re(opts.pattern)
    #print((fmt_as_re))

    try:
	if opts.filename:
    	    with open(opts.filename, "rt") as f:
		input = f.readline().strip()
	else:
	    input = sys.stdin.readline().strip()
    except Exception as e:
    	""" Be carefull no warning will be issued or insert print statement below """
	print("Error: %s" % e)
    	major = 0
    	minor = 0
    	build = 0
    #print(("Input=%s" % input))
    try:
	m = re.match(fmt_as_re,input)
	gd = m.groupdict()
	major = int(gd['major'])
	minor = int(gd['minor'])
	build = int(gd['build'])
    except:
    	major = 0
    	minor = 0
    	build = 0

    if opts.zero:
        major = 0
        minor = 0
        build = 1
    if opts.incr_major:
        major += 1
        minor = 0
        build = 1
    if opts.incr_minor:
        minor += 1
        build = 1
    if opts.incr_build:
        build += 1
    output = opts.pattern.format(M=major, m=minor, b=build)
    #print(("Outpt=%s" % output))
    try:
	with open(opts.filename, "wt") as f:
    	    f.write(output)
    except:
	print((output))
    sys.exit(0)
