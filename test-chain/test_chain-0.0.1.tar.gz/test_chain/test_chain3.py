from .test_chain_meta import TestChainMeta
import unittest

class TestChain(unittest.TestCase, metaclass=TestChainMeta):
    """
    Creates an instance of a testChain class for easy implementation through extension
    This particular instance is created in the syntax of Python 3.5 to account for slight
    variations in the use of metaclasses between versions
    """
