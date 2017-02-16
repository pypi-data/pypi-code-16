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
import shutil


class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        siteroot = "/tmp/siteroot"
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree(siteroot, ignore_errors=True)
        dbpath = "%s/var/lib/db/packages.db" % siteroot
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        self.siteroot = siteroot
        self._mgr = Installer(siteroot)

    def tearDown(self):
        pass

    def testInstallerNoDeps(self):
        ''' Check if the instalation can be done without deps'''
        self._mgr = Installer(self.siteroot)
        packages = list(self._mgr.remoteListPackages(
            "LCG_84_neurobayes_3.7.0_x86_64_slc6_gcc49_opt"))
        self._mgr._install(packages, justdb=True)
        res_normal = self._mgr._localDB.dbStats()

        shutil.rmtree(self.siteroot, ignore_errors=True)
        self._mgr = Installer(self.siteroot)
        packages = list(self._mgr.remoteListPackages(
            "LCG_84_neurobayes_3.7.0_x86_64_slc6_gcc49_opt"))
        self._mgr._install(packages, justdb=True, nodeps=True)
        res_install_nodeps = self._mgr._localDB.dbStats()

        shutil.rmtree(self.siteroot, ignore_errors=True)
        self._mgr = Installer(self.siteroot, nodeps=True)
        packages = list(self._mgr.remoteListPackages(
            "LCG_84_neurobayes_3.7.0_x86_64_slc6_gcc49_opt"))
        self._mgr._install(packages, justdb=True)
        res_nodeps = self._mgr._localDB.dbStats()
        self.assertNotEqual(res_normal[0], res_install_nodeps[0],
                            "Checking if the number of install packages with "
                            "deps is different from the number of packages "
                            "install without deps")
        self.assertEqual(res_nodeps[0], res_install_nodeps[0],
                         "Checking the number of install packages with local "
                         " nodeps flag is the same as with the global"
                         " configuration nodeps flag")

    def testFindProvides(self):
        ''' Check that we can filter the list of provides in the DB '''
        ps = list(self._mgr.remoteListProvides("BRUNEL_v51r0"))
        self.assertEqual(len(ps), 11,
                         "Checking the number of provides for BRUNEL v51r0")

    def testFindDeps(self):
        '''  Check we can locate a package and its dependencies '''
        packages = self._mgr \
                       .remoteFindPackage("BRUNEL_v51r0_x86_64_slc6_gcc49_opt")
        for p in packages:
            url = p.url()
            refurl = "http://lhcbproject.web.cern.ch/lhcbproject/dist/rpm/" \
                     "lhcb/BRUNEL_v51r0_x86_64_slc6_gcc49_opt-1.0.0-1" \
                     ".noarch.rpm"
            self.assertEqual(url, refurl, "Is package URL correct")

    def testListPackages(self):
        '''  Test the list of packages '''
        packages = self._mgr.remoteListPackages("BRUNEL_v51r0")
        allp = list(packages)
        self.assertEquals(len(allp), 9,
                          "Check that we have 9 packages for v51r0")

    def testListpackagesToInstall(self):
        '''
        test the procedure that queries for the list of packages to install
        '''
        plist = self._mgr\
                    .remoteFindPackage("BRUNEL_v51r0_x86_64_slc6_gcc49_opt")
        p = plist[0]

        toinstall = self._mgr \
                        ._getPackagesToInstall(p)
        print(len(toinstall))
        for p, _ in toinstall:
            print(p.rpmName())
        return
        # self.assertEqual(len(toinstall), 125,
        #                  "Brunel v51r0 requires 125 packages on an empty DB")

        # Now faking the insertion of xapian-e16be_1.2.21_x86_64_slc6_gcc49_opt
        from lbinstall.DependencyManager import Provides, Package
        xapname = "xapian-e16be_1.2.21_x86_64_slc6_gcc49_opt"
        xapver = "1.0.0"
        xaprel = "1"
        self._mgr._localDB.addPackage(Package(xapname, xapver, xaprel,
                                              group="LCG",
                                              provides=[Provides(xapname,
                                                                 xapver,
                                                                 xaprel)]),
                                      {"metadata": "None"})
        toinstall = self._mgr._getPackagesToInstall(p)
        print(len(toinstall))
        self.assertEqual(len(toinstall), 124,
                         "Brunel v51r0 requires 124 packages when xapian is"
                         "there")

        # Now faking the insertion of the whole of LCG plus LHCb up to REC:

        for xapname in ["LCG_84_Python_2.7.10_x86_64_slc6_gcc49_opt",
                        "LCG_84_HepMC_2.06.09_x86_64_slc6_gcc49_opt",
                        "LCGCMT_LCGCMT_84",
                        "REC_v20r0_x86_64_slc6_gcc49_opt"]:

            xapver = "1.0.0"
            xaprel = "1"
            self._mgr._localDB.addPackage(Package(xapname, xapver, xaprel,
                                                  group="LHCb",
                                                  provides=[Provides(xapname,
                                                                     xapver,
                                                                     xaprel)]),
                                          {"metadata": "None"})

        toinstall = self._mgr._getPackagesToInstall(p)
        print(len(toinstall))
        from pprint import pprint
        # pprint([p.name for p in toinstall])
        self.assertEqual(len(toinstall), 13,
                         "At this point 13 packages should be needed")

    def testFindFile(self):
        locdir = os.path.dirname(__file__)
        testfilepath = os.path.abspath(os.path.join(locdir,
                                                    "dir1",
                                                    "dir3",
                                                    "testfile.txt"))
        res = findFileInDir("testfile.txt", locdir)
        self.assertEquals(res, testfilepath, "Problem finding file in path")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
