#-*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

from typy.google.protobuf import descriptor, descriptor_pb2

try:
	import _typy
except ImportError:
	_typy = None


class MetaEnum(type):
	Enums = {}
	_builtin_attrs = frozenset([
		'__class__', '__cmp__', '__del__', '__delattr__',
		'__dir__', '__doc__', '__getattr__', '__getattribute__', '__hash__',
		'__init__', '__metaclass__', '__module__', '__new__', '__reduce__',
		'__reduce_ex__', '__repr__', '__setattr__', '__slots__', '__str__',
		'__weakref__', '__dict__', '__members__', '__methods__',
		'__qualname__', '__unicode__'
	])

	def __new__(mcs, clsname, bases, attrs):
		enum = {}
		hasZero = False
		for k, v in attrs.iteritems():
			if k in mcs._builtin_attrs: continue
			if isinstance(v, int):
				enum[k] = (v, "")
			elif isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], int):
				if len(v) == 1:
					enum[k] = v + ("", )
				else:
					enum[k] = v
			else:
				raise TypeError, "Named constant %r expected an int value with an optional name string, but got %r" % (k, v)
			if enum[k][0] == 0:
				hasZero = True

		if not hasZero and clsname != 'Enum':
			raise TypeError, "The enum '%s' must have a zero value." % clsname

		if clsname in mcs.Enums:
			raise TypeError, 'Enum name "%s" already exists.' % clsname

		for k in enum.iterkeys():
			del attrs[k]
		attrs.setdefault('__slots__', ())
		cls = super(MetaEnum, mcs).__new__(mcs, clsname, bases, attrs)
		cls.__enum__ = {}
		cls.__DESCRIPTOR__ = None
		for k, v in enum.iteritems():
			e = cls(v[0])
			e.name = k
			e.label = v[1]
			setattr(cls, k, e)
			cls.__enum__[v[0]] = e

		if clsname != 'Enum':
			mcs.Enums[clsname] = cls
			if _typy is not None and hasattr(_typy, clsname):
				getattr(_typy, clsname)(cls.__enum__)

		return cls

	def __call__(cls, value = 0, **metadata):
		if value in cls.__enum__:
			return cls.__enum__[value]
		return super(MetaEnum, cls).__call__(value)

	@property
	def DESCRIPTOR(cls):
		if cls.__DESCRIPTOR__ is not None:
			return cls.__DESCRIPTOR__

		proto = descriptor_pb2.FileDescriptorProto()
		proto.name = 'typy.%s' % cls.__name__
		proto.package = 'typy'
		proto.enum_type.add(name = cls.__name__)
		for i, v in cls.__enum__.iteritems():
			proto.enum_type[-1].value.add(name = v.name, number = i)

		if hasattr(proto, 'syntax'):
			proto.syntax = 'proto3'
			descriptor.FileDescriptor(name = proto.name, package = proto.package,
				serialized_pb = proto.SerializeToString(), syntax = proto.syntax)
		else:
			descriptor.FileDescriptor(name = proto.name, package = proto.package,
				serialized_pb = proto.SerializeToString())

		cls.__DESCRIPTOR__ = descriptor.EnumDescriptor(
			name = cls.__name__, full_name = 'typy.%s' % cls.__name__,
			values = [descriptor.EnumValueDescriptor(name = v.name, index = i, number = i, options = None, type=None) for i, v in cls.__enum__.iteritems()],
			filename = None, file = None, containing_type = None, options = None,
			serialized_start = None, serialized_end = None)

		return cls.__DESCRIPTOR__


class Enum(int):
	__metaclass__ = MetaEnum
	__slots__ = 'name', 'label'

	def __repr__(self):
		return "%s.%s" % (self.__class__.__name__, self.name)

	def __unicode__(self):
		if isinstance(self.label, str):
			return self.label.decode('utf-8')
		return self.label

	def __str__(self):
		if isinstance(self.label, unicode):
			return self.label.encode('utf-8')
		return self.label
