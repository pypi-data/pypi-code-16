#!/usr/bin/env python

import sys

def availablePackages():
    """
      Lists the available Python related packages in the distribution.
    """
    dict = {}
    for dist in __import__('pkg_resources').working_set:
        key = dist.project_name
        val = dist.version
        dict[key] = val

    print "__________________________________________________"
    print "No.   Name:                 Version: "
    print "--------------------------------------------------"
    i = 1
    for key in sorted(dict.iterkeys()):
        print "%-5i %-20s  %-10s" %( i, key, dict[key])
        i += 1
    print "__________________________________________________"

if __name__ == "__main__":
   availablePackages()
