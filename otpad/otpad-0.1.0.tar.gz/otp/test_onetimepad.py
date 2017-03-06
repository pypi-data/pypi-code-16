import unittest
from onetimepad import onetimepad
from cryptography.fernet import Fernet


class TestOnetimepad(unittest.TestCase):

    def test_string_lengths_must_match(self):
        with self.assertRaises(AssertionError):
            onetimepad('abc', 'defg')

    def test_keys_are_retrievable(self):
        k1 = Fernet.generate_key()
        k2 = Fernet.generate_key()
        encrypted = onetimepad(k1, k2)
        self.assertEqual(k1, onetimepad(encrypted, k2))

    def test_symmetry_of_onetime_pad(self):
        k1 = Fernet.generate_key()
        k2 = Fernet.generate_key()
        encrypted = onetimepad(k1, k2)
        self.assertEqual(k1, onetimepad(encrypted, k2))
        self.assertEqual(k1, onetimepad(k2, encrypted))
        self.assertEqual(k2, onetimepad(k1, encrypted))
        self.assertEqual(k2, onetimepad(encrypted, k1))
