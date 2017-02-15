#*    pyx509 - Python library for parsing X.509
#*    Copyright (C) 2009-2012  CZ.NIC, z.s.p.o. (http://www.nic.cz)
#*
#*    This library is free software; you can redistribute it and/or
#*    modify it under the terms of the GNU Library General Public
#*    License as published by the Free Software Foundation; either
#*    version 2 of the License, or (at your option) any later version.
#*
#*    This library is distributed in the hope that it will be useful,
#*    but WITHOUT ANY WARRANTY; without even the implied warranty of
#*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#*    Library General Public License for more details.
#*
#*    You should have received a copy of the
#*    GNU Library General Public License along with this library;
#*    if not, write to the Free Foundation, Inc.,
#*    51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#*

import os
from os.path import join
from io import StringIO
import sys
import unittest

from x509 import commands

TEST_DATA_DIR = join(os.path.dirname(__file__), 'data')
TEST_CERTIFICATE = join(TEST_DATA_DIR, 'test_certificate.der')
TEST_CERTIFICATE_TXT = join(TEST_DATA_DIR, 'test_certificate.txt')
TEST_SIGNATURE = join(TEST_DATA_DIR, 'test_signature.der')
TEST_SIGNATURE_TXT = join(TEST_DATA_DIR, 'test_signature.txt')
TEST_TIMESTAMP = join(TEST_DATA_DIR, 'test_timestamp.der')
TEST_TIMESTAMP_TXT = join(TEST_DATA_DIR, 'test_timestamp.txt')
TEST_TIMESTAMP_INFO_TXT = join(TEST_DATA_DIR, 'test_timestamp_info.txt')


class SimpleTest(unittest.TestCase):

    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_certificate(self):
        with open(TEST_CERTIFICATE, 'rb') as fh:
            commands.print_certificate_info(fh.read())
        txt1 = sys.stdout.getvalue()
        with open(TEST_CERTIFICATE_TXT, 'r') as fh:
            txt2 = fh.read()
        self.maxDiff = 4096
        self.assertEqual(txt1, txt2)

    def test_signature(self):
        with open(TEST_SIGNATURE, 'rb') as fh:
            commands.print_signature_info(fh.read())
        txt1 = sys.stdout.getvalue()
        with open(TEST_SIGNATURE_TXT, 'r') as fh:
            txt2 = fh.read()
        self.maxDiff = 8192
        self.assertEqual(txt1, txt2)

    def test_timestamp(self):
        with open(TEST_TIMESTAMP, 'rb') as fh:
            commands.print_signature_info(fh.read())
        txt1 = sys.stdout.getvalue()
        with open(TEST_TIMESTAMP_TXT, 'r') as fh:
            txt2 = fh.read()
        self.maxDiff = 4096
        self.assertEqual(txt1, txt2)

    def test_timestamp_info(self):
        with open(TEST_TIMESTAMP, 'rb') as fh:
            commands.print_timestamp_info(fh.read())
        txt1 = sys.stdout.getvalue()
        with open(TEST_TIMESTAMP_INFO_TXT, 'r') as fh:
            txt2 = fh.read()
        self.maxDiff = 4096
        self.assertEqual(txt1, txt2)


if __name__ == '__main__':
    unittest.main()
