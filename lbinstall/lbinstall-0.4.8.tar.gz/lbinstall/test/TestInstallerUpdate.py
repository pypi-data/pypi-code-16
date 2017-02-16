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

Test of the update functionality

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

    def testInstallUpdate(self):
        '''
        test the procedure that queries for the list of packages to install
        '''
        pnames = [("MOORE_v25r4", "1.0.0", "1"),
                  ("MOORE_v25r4_index", "1.0.0", "1"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_opt", "1.0.0", "1"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_dbg", "1.0.0", "1")]

        self._mgr.install(pnames)
        for pname, ver, rel in pnames:
            packagelist = self._mgr.remoteFindPackage(pname, ver, rel)
            lpacks = list(self._mgr.localFindPackages(pname,
                                                      exact_search=True))
            self.assertEqual(len(lpacks), 1,
                             "There should be one match for %s" % pname)
            lp0 = lpacks[0]
            self.assertEqual(lp0.name, pname,
                             "Not matching: %s/%s" % (pname, lp0.name))
            self.assertEqual(lp0.version, ver,
                             "Not matching: %s/%s" % (ver, lp0.version))
            self.assertEqual(lp0.release, rel,
                             "Not matching: %s/%s" % (rel, lp0.release))

        pnames = [("MOORE_v25r4", "1.0.0", "2"),
                  ("MOORE_v25r4_index", "1.0.0", "1"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_opt", "1.0.0", "1"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_dbg", "1.0.0", "1")]

        self._mgr.update(pnames)
        for pname, ver, rel in pnames:
            packagelist = self._mgr.remoteFindPackage(pname, ver, rel)
            lpacks = list(self._mgr.localFindPackages(pname,
                                                      exact_search=True))
            self.assertEqual(len(lpacks), 1,
                             "There should be one match for %s" % pname)
            lp0 = lpacks[0]
            self.assertEqual(lp0.name, pname,
                             "Not matching: %s/%s" % (pname, lp0.name))
            self.assertEqual(lp0.version, ver,
                             "Not matching: %s/%s" % (ver, lp0.version))
            self.assertEqual(lp0.release, rel,
                             "Not matching: %s/%s" % (rel, lp0.release))

        pnames = [("MOORE_v25r4", "1.0.0", "2"),
                  ("MOORE_v25r4_index", "1.0.0", "2"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_opt", "1.0.0", "2"),
                  ("MOORE_v25r4_x86_64_slc6_gcc49_dbg", "1.0.0", "2")]

        self._mgr.update(pnames)
        for pname, ver, rel in pnames:
            packagelist = self._mgr.remoteFindPackage(pname, ver, rel)
            lpacks = list(self._mgr.localFindPackages(pname,
                                                      exact_search=True))
            self.assertEqual(len(lpacks), 1,
                             "There should be one match for %s" % pname)
            lp0 = lpacks[0]
            self.assertEqual(lp0.name, pname,
                             "Not matching: %s/%s" % (pname, lp0.name))
            self.assertEqual(lp0.version, ver,
                             "Not matching: %s/%s" % (ver, lp0.version))
            self.assertEqual(lp0.release, rel,
                             "Not matching: %s/%s" % (rel, lp0.release))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
