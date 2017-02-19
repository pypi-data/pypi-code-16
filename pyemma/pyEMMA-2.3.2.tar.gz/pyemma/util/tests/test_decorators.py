import unittest

from pyemma.util.annotators import fix_docs

from abc import ABCMeta
class A(ABCMeta):

    def foo(self):
        """boring docstring"""
    @property
    def bar(self):
        """boring docstring"""

@fix_docs
class B(A):

    def foo_bar(self):
        """yes"""

@fix_docs
class C(B):
    def foo(self):
        pass

class TestFixDocs(unittest.TestCase):
    def test(self):
        assert B.foo.__doc__ == "boring docstring"
        assert B.bar.__doc__ == "boring docstring"
        assert C.foo.__doc__ == "boring docstring"