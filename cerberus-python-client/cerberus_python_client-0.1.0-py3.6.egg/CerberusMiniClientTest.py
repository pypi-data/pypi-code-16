#!/usr/bin/python
from client import CerberusClient
cerberus = CerberusClient('https://prod.cerberus.nikecloud.com', 'ann.wallace@nike.com', 'Un1c0rn!')

token = cerberus.get_token()

auth = cerberus.get_auth()

print (auth)
print(token)

path = cerberus.get_sdb_path('Okta')

keys = cerberus.get_sdb_keys(path)
print("KEYS", keys)

secret = cerberus.get_secret(path + '/api_key', 'nike.oktapreview.com')

print(secret)
