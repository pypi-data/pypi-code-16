import unittest
import otpad
from cryptography.fernet import Fernet
import base64


class TestOnetimepad(unittest.TestCase):

    def test_string_lengths_must_match(self):
        with self.assertRaises(AssertionError):
            otpad.pad('abc', 'defg')
            otpad.unpad('abc', 'defg')

    def test_keys_are_retrievable(self):
        k1 = Fernet.generate_key()
        k2 = Fernet.generate_key()
        encrypted = otpad.pad(k1, k2)
        orig = otpad.unpad(k1, encrypted['encrypted'])
        self.assertEqual(k2, orig['decrypted'])

    def test_hmac_encryption_and_retrieval(self):
        k1 = Fernet.generate_key()
        k2 = Fernet.generate_key()
        k3 = Fernet.generate_key()

        padded = otpad.pad(k1, k2, hmac_key=k3)
        orig = otpad.unpad(k1,
                           padded['encrypted'],
                           hmac_key=k3,
                           hmac_digest=padded['digest'])
        self.assertEqual(orig['decrypted'], k2)

    def test_invalid_hmac_key_raises_exception(self):
        with self.assertRaises(Exception):
            k1 = Fernet.generate_key()
            k2 = Fernet.generate_key()
            k3 = Fernet.generate_key()
            padded = otpad.pad(k1, k2, hmac_key=k3)
            orig = otpad.unpad(k1,
                               padded['encrypted'],
                               hmac_key='213rwefgsdfywergsdfgsdfgd',
                               hmac_digest=padded['digest'])


    def test_invalid_hmac_digest_raises_exception(self):
        with self.assertRaises(Exception):
            k1 = Fernet.generate_key()
            k2 = Fernet.generate_key()
            k3 = Fernet.generate_key()
            padded = otpad.pad(k1, k2, hmac_key=k3)
            orig = otpad.unpad(k1,
                               padded['encrypted'],
                               hmac_key=k3,
                               hmac_digest='213rwefgsdfywergsdfgsdfgd')