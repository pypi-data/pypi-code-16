#!/usr/bin/env python

"""
Script to generate config information for python
$Id: generateLibCFConfig.py 960 2016-09-06 08:50:06Z pletzer $
"""

from __future__ import print_function
import re
import time
import os.path
from argparse import ArgumentParser
import sys

UNSET_VALUE = '123456790'

FMT = """
try:
    {0} = {1}
except:
    {0} = None
"""

# parse command line arguments
parser = ArgumentParser(description='Generate libCF python configuration file')
parser.add_argument("-l", "--netcdf_libdir", dest="netcdf_libdir",
                    help="directory where netcdf library resides")
parser.add_argument("-i", "--netcdf_incdir", dest="netcdf_incdir",
                    help="directory where netcdf.h resides")
parser.add_argument("-b", "--builddir", dest="builddir",
                    help="location of build directory",)
parser.add_argument("-s", "--srcdir", dest="srcdir",
                    help="location of source directory",)
parser.add_argument("-c", "--config", dest="config",
                    help="path to python config file (output)",)
options = parser.parse_args()

def parseHeader(filename):
    nameValue = []
    for oline in open(filename).readlines():
        line = oline.rstrip()

        # 	NC_INT =	4,	/* signed 4 byte integer */
        m = re.match(r'^\s*(NC_\w+)\s*=\s*(\d+)\,?', line)
        if m:
            name, value = m.group(1), m.group(2)
            nameValue.append([name, value])

        if not re.search(r'#define', line): continue
        # don't know what to do with
        if re.search(r'size\_t', line): continue
        # removing casting
        line = re.sub(r'\(\s*char\s*\*\s*\)', '', line)
        line = re.sub(r'\(\s*char\s*\)', '', line)
        line = re.sub(r'\(\s*signed\s+char\s*\)', '', line)
        line = re.sub(r'\(\s*short\s*\)', '', line)
        line = re.sub(r'\(\s*long\s+long\s*\)', '', line)
        line = re.sub(r'\(\s*unsigned\s+long\s+long\s*\)', '', line)
        # remove trailing comment 
        line = re.sub(r'\s*\/\*.*\*?\/?', '', line)
        # remove parentheses around numbers, as in #define NC_EMAXNAME    	(-53)
        line = re.sub(r'\(([^\)]+)\)', '\\1', line)
        # remove trailing f, as in #define NC_MAX_FLOAT 3.402823466e+38f
        line = re.sub(r'e(\-?\+?\d+)f\s*$', 'e\\1', line)
        # remove LL from #define NC_MAX_INT64  9223372036854775807LL
        line = re.sub(r'\s+(\-?\d+)U?L?L?', ' \\1', line)
        # Find the name and value pair
        f1 = '^#define\s+([A-Z\_\d]+)\s+\(?(\"?[!@#$%^&*()|:%\\\/\-\w\d\+\., ]*\"?)\)?\s*' 
        m = re.match(f1, line)
        if m:
           name, value = m.group(1), m.group(2)
           nameValue.append([name, value])
    return nameValue

# parse netcdf header
print(options.netcdf_incdir)
netcdf_header = options.netcdf_incdir + '/netcdf.h'
nc_constants = parseHeader(netcdf_header)

# libcf headers
libcf_headers = [options.srcdir + '/include/libcf_src.h',
                 options.srcdir + '/include/nccf_constants.h',
                 options.srcdir + '/include/nccf_errors.h',
                 ]
libcf_constants = []
for header in libcf_headers:
    libcf_constants += parseHeader(header)

# generate configure information and save it
cfg = open(options.config, 'w')
cmd = sys.argv[0]
for a in sys.argv[1:]:
    cmd += ' ' + a
print("""
# DO NOT EDIT THIS FILE!
# This script was auto-generated by running the command:
# {0}
# {1}
""".format(cmd, time.asctime()), file=cfg)

# location of the netcdf library
print('netcdf_libdir = "{}"'.format(options.netcdf_libdir), file=cfg)
print('netcdf_incdir = "{}"'.format(options.netcdf_incdir), file=cfg)

print('# netcdf constants', file=cfg)
for c in nc_constants:
    try:
        num = eval(c[1])
        print('{0} = {1}'.format(c[0], c[1]), file=cfg)
    except:
        print(FMT.format(c[0], c[1], c[0]), file=cfg)

print('# libCF constants', file=cfg)
for c in libcf_constants:
    try:
        num = eval(c[1])
        print('{0} = {1}'.format(c[0], c[1]), file=cfg)
    except:
        print(FMT.format(c[0], c[1], c[0]), file=cfg)

cfg.close()
