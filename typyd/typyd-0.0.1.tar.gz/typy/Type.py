#-*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

import sys
_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode('latin1'))

from Enum import MetaEnum, Enum as _Enum

def isEnum(cls):
	return isinstance(cls, type) and issubclass(cls, _Enum)

try:
	import _typy
except ImportError:
	_typy = None


class MetaType(type):
	typesDict = {}

	def __new__(mcs, clsname, bases, attrs):
		if clsname != 'Enum' and 'Enum' in mcs.typesDict and mcs.typesDict['Enum'] in bases:
			return MetaEnum(clsname, (_Enum, ), attrs)
		if '____realType__' not in attrs:
			attrs['____realType__'] = True
		attrs['__name__'] = clsname
		cls = super(MetaType, mcs).__new__(mcs, clsname, bases, attrs)
		if cls.____realType__:
			mcs.typesDict[cls.__name__] = cls
		return cls

	def getType(cls, clsname):
		return cls.typesDict.get(clsname)


class Type(object):
	__metaclass__ = MetaType
	__slots__ = 'metadata'
	____realType__ = False
	____keywords__ = ()

	def __init__(self, **metadata):
		self.metadata = metadata


def toType(t):
	if isinstance(t, (list, tuple, set)):
		if len(t) > 1:
			return Instance(*t)
		else:
			t = tuple(t)[0]
	if isinstance(t, type):
		if issubclass(t, Type):
			t = t()
		elif issubclass(t, _Enum):
			t = Enum(t)
		else:
			t = Instance(t)
	assert isinstance(t, Type)
	return t


class Simple(Type):
	____realType__ = False


class Integer(Simple):
	default = 0
	pyType = int
	pbType = 'int32'

	def __str__(self):
		return '[Type:Integer%s]' % repr(self.metadata)


class Float(Simple):
	default = 0.0
	pyType = float
	pbType = 'float'

	def __str__(self):
		return '[Type:Float%s]' % repr(self.metadata)


class Double(Simple):
	default = 0.0
	pyType = float
	pbType = 'double'

	def __str__(self):
		return '[Type:Double%s]' % repr(self.metadata)


class FixedPoint(Simple):
	__slots__ = 'floor', 'precision'
	default = 0.0
	pyType = float
	pbType = 'double'

	def __init__(self, precision = 0, floor = 0, **metadata):
		self.floor = floor
		self.precision = precision
		super(FixedPoint, self).__init__(**metadata)

	def __str__(self):
		return '[Type:FixedPoint<%d, %d>%s]' % (self.precision, self.floor, repr(self.metadata))


class Boolean(Simple):
	default = False
	pyType = bool
	pbType = 'bool'

	def __str__(self):
		return '[Type:Boolean%s]' % repr(self.metadata)


class String(Simple):
	default = _b("").decode('utf-8')
	pyType = str
	pbType = 'string'

	def __str__(self):
		return '[Type:String%s]' % repr(self.metadata)


class Bytes(Simple):
	default = _b("")
	pyType = str
	pbType = 'bytes'

	def __str__(self):
		return '[Type:Bytes%s]' % repr(self.metadata)


class _Python(Type):
	__slots__ = 'pyType', '__name__'
	default = None
	pbType = 'message'

	def __init__(self, pyType, **metadata):
		self.pyType = pyType if isinstance(pyType, type) else type(pyType)
		self.__name__ = self.pyType.__name__
		if _typy is not None and hasattr(_typy, self.__name__):
			getattr(_typy, self.__name__)(self.pyType)
		super(_Python, self).__init__(**metadata)

	def __str__(self):
		return '[Type:Python(%s, %s)]' % (self.pyType.__name__, repr(self.metadata))

Python = type('Python', (_Python,), {})
MetaType.typesDict['Python'] = Python


class Instance(Type):
	__slots__ = 'pyType',
	default = None
	pbType = 'message'

	def __init__(self, *pyType, **metadata):
		pyType = tuple(reduce(lambda a, b: a | set(b.pyType), (p for p in pyType if isinstance(p, Instance)), set((p for p in pyType if not isinstance(p, Instance)))))
		assert not tuple((p for p in pyType if p is not None and not isinstance(p, (type, Type))))
		self.pyType = pyType
		super(Instance, self).__init__(**metadata)

	def __str__(self):
		return '[Type:Object(%s, %s)]' % ([p.__name__ for p in self.pyType], repr(self.metadata))


class Enum(Type):
	__slots__ = 'pyType',
	default = 0
	pbType = 'enum'

	def __init__(self, pyType, **metadata):
		assert isEnum(pyType)
		self.pyType = pyType
		super(Enum, self).__init__(**metadata)

	def __str__(self):
		return '[Type:Enum(%s, %s)]' % (self.pyType.__name__, repr(self.metadata))


class Collection(Type):
	____realType__ = False


class List(Collection):
	__slots__ = 'elementType'
	default = []
	pyType = list

	@property
	def pbType(self):
		return self.elementType.pbType

	def __init__(self, *elementType, **metadata):
		if len(elementType) == 1 and isinstance(elementType[0], (list, tuple, set)):
			self.elementType = toType(elementType[0])
		else:
			self.elementType = toType(elementType)
		super(List, self).__init__(**metadata)

	def __str__(self):
		return '[Type:List(%s, %s)]' % (str(self.elementType), repr(self.metadata))


class Dict(Collection):
	__slots__ = 'keyType', 'valueType'
	default = {}
	pyType = dict
	pbType = 'message'

	def __init__(self, keyType, *valueType, **metadata):
		self.keyType = toType(keyType)
		if len(valueType) == 1 and isinstance(valueType[0], (list, tuple, set)):
			self.valueType = toType(valueType[0])
		else:
			self.valueType = toType(valueType)
		super(Dict, self).__init__(**metadata)

	def __str__(self):
		return '[Type:Dict(%s, %s, %s)]' % (str(self.keyType), str(self.valueType), repr(self.metadata))


class MetaKeyword(type):
	____keywords__ = {}

	def __new__(mcs, clsname, bases, attrs):
		cls = super(MetaKeyword, mcs).__new__(mcs, clsname, bases, attrs)
		mcs.____keywords__[clsname] = cls
		return cls

	def __getattr__(cls, name):
		return getattr(cls(), name)


class Keyword(object):
	__metaclass__ = MetaKeyword

	def __init__(self, leadingKeyword = None):
		self.____leadingKeyword__ = leadingKeyword

	def __getattr__(self, item):
		keyword = MetaKeyword.____keywords__.get(item)
		if keyword:
			return keyword(self)
		else:
			t = Type.getType(item)
			if t:
				allKeywords = set()
				allKeywords.add(self.__class__)
				keyword = self.____leadingKeyword__
				while keyword:
					allKeywords.add(keyword.__class__)
					keyword = keyword.____leadingKeyword__
				decoratedPropType = type(t.__name__, (t,), {"____keywords__": tuple(allKeywords)})
				return decoratedPropType
			else:
				raise AttributeError("%r is neither a keyword nor a property type." % item)


class pb(Keyword): pass
