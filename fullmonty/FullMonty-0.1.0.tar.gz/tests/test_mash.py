# coding=utf-8

"""
Test Mash
"""
from fullmonty.mash import Mash

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyMethodMayBeStatic
class TestMash(object):
    """
    Test the Mash class
    """

    def test_basic_dict(self):
        """
        basic functionality
        """
        a = Mash()
        assert len(a) == 0
        a['foo'] = 'bar'
        assert len(a) == 1
        assert a['foo'] == 'bar'
        assert a.foo == 'bar'
        a['foo'] = 'fig'
        assert len(a) == 1
        assert a['foo'] == 'fig'
        assert a.foo == 'fig'
        del a['foo']
        assert len(a) == 0

    def test_basic_namespace(self):
        """
        basic functionality
        """
        a = Mash()
        assert len(a) == 0
        a.foo = 'bar'
        assert len(a) == 1
        assert a['foo'] == 'bar'
        assert a.foo == 'bar'
        a.foo = 'fig'
        assert len(a) == 1
        assert a['foo'] == 'fig'
        assert a.foo == 'fig'
        del a.foo
        assert len(a) == 0

    def test_identitiy(self):
        """
        test identity
        """
        a = Mash()
        a.foo = 'bar'
        assert a['foo'] == a.foo
        assert a.foo == a['foo']

    def test_keys(self):
        """
        test dict.keys
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        assert len(a) == 3
        assert len(a.keys()) == 3
        assert set(a.keys()) == {'foo', 'bar', 'fig'}

    def test_copy_constructor(self):
        """
        test copy constructor
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        b = Mash(a)
        assert len(b) == 3
        assert len(b.keys()) == 3
        assert set(b.keys()) == {'foo', 'bar', 'fig'}

    def test_delattr(self):
        """
        test delattr
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        assert set(a.keys()) == {'foo', 'bar', 'fig'}
        delattr(a, 'bar')
        assert set(a.keys()) == {'foo', 'fig'}

    def test_invalid_attribute_name_keys(self):
        """
        These keys are accessible only via dict accessors.  You can not use attribute accessors.
        :return:
        :rtype:
        """
        a = Mash()
        a[1] = 'foo'
        a['a*b'] = 'bar'
        a['c.d'] = 'fig'
        assert a[1] == 'foo'
        assert a['a*b'] == 'bar'
        assert a['c.d'] == 'fig'
