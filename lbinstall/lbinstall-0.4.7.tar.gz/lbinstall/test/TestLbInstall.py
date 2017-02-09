'''
Created on 12 Jan 2017

@author: Stefan Chitic
'''
import os
import unittest
import logging

from lbinstall.LbInstall import LbInstallException
from lbinstall.LbInstall import LbInstallOptionParser
from lbinstall.LbInstall import LbInstallClient
from lbinstall.LbInstall import LbInstall
from lbinstall.LbInstall import usage


class Test(unittest.TestCase):

    def setUp(self):
        self.parser = LbInstallOptionParser()

    def tearDown(self):
        pass

    def testClientMode(self):
        """ Test if the client mode is parsed corectly"""
        arguments = ['--dry-run', '--root=/tmp/siteroot/']
        args = arguments + ['inexisting_mode', 'rpm']
        try:
            self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                                   prog="LbInstall",
                                                   arguments=args)
            r = self.lbInstallClient.main()
        except LbInstallException as e:
            self.assertEqual(str(e), ("Unrecognized command: "
                                      "inexisting_mode"))
            self.assertEqual(r, 1)
        for opt in ['install', 'query', 'list', 'remove', 'update']:
            print("Trying:", opt)
            args = arguments + [opt, 'CMT']
            self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                                   prog="LbInstall",
                                                   arguments=args)
            r = self.lbInstallClient.main()
            self.assertEqual(r, 0)
        for opt in ['remove']:
            args = arguments + [opt]
            self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                                   prog="LbInstall",
                                                   arguments=args)
            try:
                r = self.lbInstallClient.main()
            except LbInstallException as e:
                self.assertEqual(str(e), ("Please specify at least the name"
                                          " of the RPM to install"))
                self.assertEqual(r, 1)
            args = arguments + [opt, "LBSCRIPTS-8.3.1-1", "8.3.1", "1"]
            self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                                   prog="LbInstall",
                                                   arguments=args)
            r = self.lbInstallClient.main()
            self.assertEqual(r, 0)

    def testOptsMain(self):
        """ Test if the arguments are parsed corectly """
        arguments = ['--debug', '--repo=repo', '--rpmcache=rpmcache',
                     '--dry-run', '--just-db',
                     '--overwrite', '--force', '--disable-update-check',
                     '--disable-yum-check', '--nodeps', '--tmp_dir=/tmp/',
                     ]
        try:
            self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                                   prog="LbInstall",
                                                   arguments=arguments)
            r = self.lbInstallClient.main()
        except LbInstallException as e:
            self.assertEqual(str(e), ("Please specify MYSITEROOT in "
                                      "the environment or use the "
                                      "--root option"))
            self.assertEqual(r, 1)
        # with os environ var
        os.environ['MYSITEROOT'] = "/tmp/siteroot/"
        arguments2 = arguments + ['--chained_database=/tmp/;/tmp/siteroot']
        self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                               prog="LbInstall",
                                               arguments=arguments2)
        try:
            r = self.lbInstallClient.main()
        except:
            self.assertEqual(r, 1)

        self.assertEqual(self.lbInstallClient.installer._siteroot,
                         '/tmp/siteroot')
        # without
        del os.environ['MYSITEROOT']
        arguments.append('--root=/tmp/siteroot/')
        arguments.append('--chained_database=/tmp/')
        self.lbInstallClient = LbInstallClient(configType="LHCbConfig",
                                               prog="LbInstall",
                                               arguments=arguments)
        try:
            self.lbInstallClient.main()
        except LbInstall as e:
            self.assertEqual(str(e), "Argument list too short")
            self.assertEqual(r, 1)
        self.assertEqual(self.lbInstallClient.installer._siteroot,
                         '/tmp/siteroot')

    def testusageFunction(self):
        msg = usage('LbInstall')
        expected = """\nLbInstall -  installs software in MYSITEROOT directory'

The environment variable MYSITEROOT MUST be set for this script to work.

It can be used in the following ways:

LbInstall install <rpmname> [<version> [<release>]]
Installs a RPM from the yum repository

LbInstall remove <rpmname> [<version> [<release>]]
Removes a RPM from the local system

LbInstall query [<rpmname regexp>]
List packages available in the repositories configured with a name
matching the regular expression passed.

LbInstall list [<rpmname regexp>]
List packages installed on the system matching the regular expression passed.

"""
        self.assertEqual(msg, expected)

    def testLbInstallFunction(self):
        ''' Test if calling lbinstall will result in
            exit code 1
        '''
        try:
            LbInstall()
        except SystemExit as cm:
            self.assertEqual(cm.code, 1)

    def testThrowException(self):
        ''' Test if the exception is thown ok'''
        e = LbInstallException("This is a test")
        self.assertTrue(isinstance(e, LbInstallException))
        self.assertEqual(str(e), "This is a test")

    def testLbInstallOptionParserExceptions(self):
        ''' Test if the parser throws the exceptions ok'''
        try:
            self.parser.error("test")
        except LbInstallException as e:
            self.assertEqual(str(e), 'Error parsing arguments: test')
        try:
            self.parser.exit(1, "test")
        except LbInstallException as e:
            self.assertEqual(str(e), 'Error parsing arguments: test')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
