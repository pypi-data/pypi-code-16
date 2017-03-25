import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from sepa_netherlands import protocol

url = 'https://machtigen.secure-ing.com/EMRoutingWS/handler/ing'

with open('priv.key') as f:
    key = f.read()
with open('cert.pem') as f:
    cert = f.read()

client = protocol.Client('TODO_MERCHANT_ID', url, url, url, key, cert)
client.request_directory()

class TestSuite(unittest.TestSuite):
    def test(self):
        return

if __name__ == '__main__':
    unittest.main()
