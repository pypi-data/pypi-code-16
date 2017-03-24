import os
import unittest

from binascii import hexlify

from m2secret import Secret

import pytest
from mock import patch


class TestSecret:
    """Verify the behavior of Secret class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.iv = 'iv_45678123456781234567812345678'
        self.salt = 'salt____123456781234567812345678'
        self.ciphertext = 'yadda yadda'
        self.iterations = 1000
        assert len(self.iv) == 32
        assert len(self.salt) == 32

    def test_ascii(self):
        secret = Secret()
        secret.encrypt('foo', 'some-key')
        res = secret.serialize()

        reverse = Secret()
        reverse.deserialize(res)
        assert reverse.decrypt('some-key') == b'foo'

    def test_unicode(self):
        secret = Secret()
        secret.encrypt(u'foo', 'some-key')
        res = secret.serialize()

        reverse = Secret()
        reverse.deserialize(res)
        assert reverse.decrypt('some-key') == b'foo'

    def test_init(self):
        secret = Secret(
            iv=self.iv,
            salt=self.salt,
            ciphertext=self.ciphertext,
            iterations=self.iterations)

        assert secret.salt == self.salt
        assert secret.iv == self.iv
        assert secret.ciphertext == self.ciphertext
        assert secret.iterations == self.iterations

    @patch.object(os, 'urandom')
    def test_default_params(self, urandom):
        """Known defaults should be used when no parameters are used."""
        urandom.return_value = 'x' * 32
        secret = Secret()
        assert len(secret.iv) == 32
        assert len(secret.salt) == 32
        urandom.assert_called_with(32)
        assert secret.ciphertext is None
        assert secret.iterations == 1000

    @pytest.mark.parametrize(('expected', 'serialized_secret'), [
        # The `serialized_secret` values were generated on different machines
        # with different openssl versions and with the old m2crypto
        # version to make sure we don't break anything.
        (
            b'super secret password string from machine 1',
            '3f3a0bd330b9b64456e7a01bf0c767268476dff84c942c58ad899c7e37c72a4c|'
            '6846b0fce9f9ae3a066f8c5ca7deb9695a80902cefdcd4e06225e2f45a2bae32|'
            'dfb7e0f57395c42e3c3520c437669430bf75d3ac728010a3c8c8e1866c73a1eeb'
            '899bec27610688c5c9557c975bbdd4d89fb931de7eeaffb80d9542e0761347dd7'
            '8d2584ad6ad2b1eb883ccb1de3ab96092fc99ba43633ab05ce2bc8f99fbe377fe'
            '843f35ac5710716dbf4a110e2fc3b'
        ),
        (
            b'super secret password string from machine 1',
            '9b27af9136b04bf4ef6a0afeb0b402925b191882f93f3fd98c12eda214e684a7|'
            '8926f70d957753d543a1e0e5c6c2da1cf2eb92d51e026fdcc971757e58e7d7e3|'
            'f7707712f1ace51733581aa638a3f612fdaab60284610fe5b3bae4df06230be71'
            '090b308581734000a3c093597288cdf7d844829932478962550ebbcb903c9e0d9'
            '0d8346d1c364f805295ef2cc669936b6ce9745188f92f4a89813b0bf0a98cbf3b'
            '9e1e60c36e841e3ac01c221f938d6'
        ),
    ])
    def test_legacy_compatibility(self, expected, serialized_secret):
        secret = Secret()
        secret.deserialize(serialized_secret)
        assert secret.decrypt('super-secret-encryption-key') == expected
