# coding=utf8
import random
import hashlib
from unittest import TestCase
from .functions import Salted

TESTCASES = [ "".join(random.sample(
    '1qazxsw23edcvfr45tgbnhy67ujmklio890pQAZXSWEDCVFRTGBNHYUJMKIOLP',
    6)
) for _ in xrange(1000)]

class TestSalted(TestCase):
    def test_gen_password (self):
        hash_methods = [hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha512]
        for hash_method in hash_methods:
            gen = Salted(hash_method)
            for case in TESTCASES:
                hashed = gen.gen_password(case)
                salt = hashed [:64]
                hash = hashed [64:]
                self.assertEqual(hash_method(":".join([salt, case])).hexdigest(), hash)


    def test_verify_password (self):
        hash_methods = [hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha512]
        for hash_method in hash_methods:
            gen = Salted(hash_method)
            for case in TESTCASES:
                hashed_pwd = gen.gen_password(case)
                self.assertEqual(gen.verify_password(case, hashed_pwd), True)
                self.assertFalse(gen.verify_password('ERROR_PASSWORD', hashed_pwd))

