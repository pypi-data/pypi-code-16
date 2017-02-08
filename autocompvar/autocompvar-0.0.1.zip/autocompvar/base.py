#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Similar to ``collections.namedtuple``, ``nameddict`` is a data container class.

**中文文档**

和 ``collections.namedtuple`` 类似, ``nameddict`` 是一种数据容器类。提供了方便的方法
对属性, 值进行for循环, 以及和list, dict之间的IO交互。
"""

try:
    from .packages import nameddict
except:
    from autocompvar.packages import nameddict

SEP = "____"


class Base(nameddict.Base):

    """nameddict base class.
    """
    __attrs__ = None
    """该属性非常重要, 定义了哪些属性被真正视为 ``attributes``, 换言之, 就是在
    :meth:`~Base.keys()`, :meth:`~Base.values()`, :meth:`~Base.items()`,
    :meth:`~Base.to_list()`, :meth:`~Base.to_dict()`, :meth:`~Base.to_OrderedDict()`,
    :meth:`~Base.to_json()`, 方法中要被包括的属性。
    """
    
    __keys__ = None
    """Indexable attribute list
    """
    
    def items(self):
        return [(key, value) for key, value in super(Base, self).items() \
                if SEP not in key]

    def _getattr_by_key_value(self, key):
        """
        """
        def getattr_by_key_value(value):
            return getattr(self, "%s____%s" % (key, value))
        return getattr_by_key_value

    def __getattr__(self, attr):
        """  

        >>> obj.getattr_by_name("John") == obj.name____John
        >>> True

        >>> obj.name____John.name == "John"
        >>> True
        """
        if attr.startswith("getattr_by_"):
            key = attr.replace("getattr_by_", "")
            return self._getattr_by_key_value(key)
        else:
            return object.__getattribute__(self, attr)
        
    
#--- Unittest ---
if __name__ == "__main__":
    class Fruit(Base):
        __attrs__ = ["id", "name"]
    
    class FruitCollection(Base):
    
        def __init__(self):
            fruit = Fruit(id=1, name="Apple")
            self.id____1 = fruit
            self.name____Apple = fruit
    
            fruit = Fruit(id=1, name="Banana")
            self.id____2 = fruit
            self.name____Banana = fruit
    
    fruit_collection = FruitCollection()
    
    def test_items():
        assert fruit_collection.keys() == []
        
    test_items()
    
    def test_getattr_by_key_value():
        assert fruit_collection.getattr_by_id(1).id == 1
        assert fruit_collection.getattr_by_name("Apple").name == "Apple"
    
    test_getattr_by_key_value()
