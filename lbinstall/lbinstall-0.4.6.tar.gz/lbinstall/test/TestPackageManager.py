'''
Created on 10 Aug 2016

@author: Ben Couturier
'''
import os
import unittest
import logging

from lbinstall.PackageManager import PackageManager


class Test(unittest.TestCase):

    def setUp(self):

        self.filename = "BRUNEL_v51r0_x86_64_slc6_gcc49_opt-1.0.0-1.noarch.rpm"
        self.url = "http://lhcbproject.web.cern.ch/lhcbproject/"\
                   "dist/rpm/lhcb/%s" % self.filename
        self.siteroot = ''
        logging.basicConfig()
        if not os.path.exists(self.filename):
            try:
                # Python 3 workaround
                import urllib.request as urllib
            except:
                import urllib
            urllib.urlretrieve(self.url, self.filename)

    def tearDown(self):
        pass

    def testGetGroup(self):
        ''' Check that we can get the group of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Group: %s" % pm.getGroup())
        self.assertEqual(pm.getGroup(), "LHCb", "Could not get group")

    def testRequires(self):
        ''' Check that we can get the list of requirements of a given RPM
        Returned as a list of triplet (reqname, reqversion, flag) '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Requires:", pm.getRequires())
        res = pm._getRequires()
        ref = [('BRUNEL_v51r0', '', None),
               ('REC_v20r0_x86_64_slc6_gcc49_opt', '', None),
               ('LCGCMT_LCGCMT_84', '', None),
               ('LCG_84_HepMC_2.06.09_x86_64_slc6_gcc49_opt', '', None),
               ('LCG_84_Python_2.7.10_x86_64_slc6_gcc49_opt', '', None),
               ('DBASE_AppConfig_v3', '', None),
               ('DBASE_FieldMap_v5', '', None),
               ('PARAM_ParamFiles_v8', '', None),
               ('DBASE_PRConfig_v1', '', None),
               ('PARAM_QMTestFiles_v1', '', None),
               ('/bin/sh', '', None),
               ('/bin/sh', '', None),
               ('rpmlib(FileDigests)', '4.6.0-1', 'LE'),
               ('rpmlib(PayloadFilesHavePrefix)', '4.0-1', 'LE'),
               ('rpmlib(CompressedFileNames)', '3.0.4-1', 'LE'),
               ('rpmlib(PayloadIsXz)', '5.2-1', 'LE')]
        self.assertEquals(res, ref, "List of requires")

    def testProvides(self):
        ''' Check that we can get the list of provides of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Provides:", pm.getProvides())
        res = pm._getProvides()
        ref = [('/bin/sh', '', None),
               ('BRUNEL_v51r0_x86_64_slc6_gcc49_opt', '1.0.0-1', 'EQ')]
        self.assertEquals(res, ref, "List of provides")

    def testGetPrefixes(self):
        ''' Check that we extract the RPM prefix properly  '''
        pm = PackageManager(self.filename, self.siteroot)
        # print("RPM Prefixes:" % pm.getPrefixes)
        ret = pm.getPrefixes()
        print("RPM Prefixes:", ret)
        ref = ['/opt/LHCbSoft']
        self.assertEquals(ret, ref, "RPM Prefix")

    def testExtract(self):
        ''' Check that we can extract a file  '''
        tmp_dir = "%s/%s" % (self.siteroot, 'tmp')
        pm = PackageManager(self.filename, self.siteroot, tmp_dir=tmp_dir)
        prefixmap = {pm.getPrefixes()[0]: "/tmp"}
        pm.setrelocatemap(prefixmap)
        pm.extract(prefixmap)
        pm.checkFileSizesOnDisk()
        pm.removeFiles()

    def testGetTopDir(self):
        ''' Check for the top directory of the files in the RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        ref = "./opt/LHCbSoft/lhcb/BRUNEL/BRUNEL_v51r0/"\
              "InstallArea/x86_64-slc6-gcc49-opt"
        self.assertEquals(pm.getTopDir(),
                          ref, "Checking the topdir for the package")

    def testGetPackage(self):
        ''' Check that we can get the list of provides of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        _res = pm.getPackage()

    def testGetFileMetadata(self):
        ''' Checks the method that returns the list of files'''
        pm = PackageManager(self.filename, self.siteroot)
        res = pm.getFileMetadata()
        self.assertTrue(len(res) == 27, "27 files and dirs in RPM")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
