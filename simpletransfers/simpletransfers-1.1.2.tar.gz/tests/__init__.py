import unittest

from testftp import testFTP
from testsftp import testSFTP
from testhttpclient import testHTTPClient
from testhttpserver import testHTTPServer
from testlocal import testLocal
from testmail import testMail
from testsoap import testSOAP
from testzip import testZipfile

def suite():
	test_suite = unittest.TestSuite()

	test_suite.addTest( unittest.makeSuite(testFTP) )
	test_suite.addTest( unittest.makeSuite(testSFTP) )
	test_suite.addTest( unittest.makeSuite(testHTTPClient) )
	test_suite.addTest( unittest.makeSuite(testHTTPServer) )
	test_suite.addTest( unittest.makeSuite(testLocal) )
	test_suite.addTest( unittest.makeSuite(testMail) )
	test_suite.addTest( unittest.makeSuite(testSOAP) )
	test_suite.addTest( unittest.makeSuite(testZipfile) )

	return test_suite

if __name__ == '__main__':
	runner = unittest.TextTestRunner()
	runner.run( suite() )
