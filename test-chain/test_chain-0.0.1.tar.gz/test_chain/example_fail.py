from .test_chain3 import TestChain
import unittest

class failure(TestChain):

    def test_skip(self):
        self.test_raise()

    def test_raise(self):
        raise not "Fail?"

if __name__ == "__main__":
    unittest.main()