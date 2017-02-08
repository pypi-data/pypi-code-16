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

Test of the Installer class

@author: Ben Couturier
'''
import logging
import os
import unittest

from lbinstall.Installer import Installer
from lbinstall.Installer import findFileInDir


class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        siteroot = "/tmp/siteroot"
        import shutil
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree(siteroot, ignore_errors=True)
        dbpath = "%s/var/lib/db/packages.db" % siteroot
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        self._mgr = Installer(siteroot, nodeps=True)

    def tearDown(self):
        pass

    def testInstallRemove(self):
        '''
        test the procedure that queries for the list of packages to install
        '''
        pnames = [("BRUNEL_v51r1", None, None)]
        self._mgr.install(pnames)
        for pname, ver, rel in pnames:
            lpacks = list(self._mgr.localFindPackages(pname,
                                                      exact_search=True))
            self.assertEqual(len(lpacks), 1,
                             "There should be one match for %s" % pname)
        self._mgr.remove(pnames)
        for pname, ver, rel in pnames:
            lpacks = list(self._mgr.localListPackages(pname))
            self.assertEqual(len(lpacks), 0,
                             "There should no match for %s" % pname)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
