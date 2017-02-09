###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Test that tries a full install of a version of Brunel in /tmp

@author: Ben Couturier
'''
import unittest

from lbinstall.Installer import Installer


class Test(unittest.TestCase):

    def setUp(self):
        import os
        import logging
        logging.basicConfig(level=logging.INFO)

        siteroot = "/tmp/siteroot"
        import shutil
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree(siteroot, ignore_errors=True)
        dbpath = "%s/var/lib/db/packages.db" % siteroot
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        self._mgr = Installer(siteroot)

    def tearDown(self):
        pass

    def testInstall(self):
        '''
        test the procedure that queries for the list of packages to install
        '''
        import os
        if os.environ.get("RUN_LONG_TESTS", None):
            pkgname = "BRUNEL_v51r0_x86_64_slc6_gcc49_opt"
            plist = self._mgr.remoteFindPackage(pkgname)
            self._mgr._install(plist)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
