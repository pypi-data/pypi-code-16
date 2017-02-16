#!/usr/bin/env python
###############################################################################
# (c) Copyright 2012-2016 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Tool to check that the rpmfile extraction is correct

@author: Ben Couturier
'''

import os
import tempfile
from lbinstall.PackageManager import PackageManager
from lbinstall.extra.RPMExtractor import extract


def checkExtraction(filename):
    ''' Extracts a given RPM with rpm2cpio an rpmfile an compares the result'''
    topdir = tempfile.mkdtemp(prefix="checkExtraction")

    rpmfiledir = os.path.join(topdir, "rpmfile")
    os.makedirs(rpmfiledir)
    cpiodir = os.path.join(topdir, "cpio")
    os.makedirs(cpiodir)

    # Extracting with rpmfile
    relocatemap = {"/opt/LHCbSoft/lhcb": rpmfiledir}
    pm = PackageManager(filename, '', relocatemap)
    pm.extract()

    # extracting with cpio
    extract([filename], cpiodir)

    cpiodir_mdata = set(extractDirInfo(cpiodir))
    rpmfiledir_mdata = set(extractDirInfo(rpmfiledir))

    # Cleaning up
    import shutil
    shutil.rmtree(cpiodir)
    shutil.rmtree(rpmfiledir)
    return(cpiodir_mdata - rpmfiledir_mdata,
           rpmfiledir_mdata - cpiodir_mdata)


def extractDirInfo(dirname):
    from os import walk, lstat
    from os.path import join, islink
    metadata = []
    for root, _dirs, files in walk(dirname):
        for f in files:
            n = join(root, f)
            sr = lstat(n)
            ret = (n.replace(dirname, ""), sr.st_size, islink(n),
                   sr.st_mode, sr.st_nlink),
            metadata.append(ret)
    return sorted(metadata)
