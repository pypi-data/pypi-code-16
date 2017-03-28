#-*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

# [joungtao] Kill magic attributes, make "composite field", "message map" and
#	"repeated composite field" can be set directly.
from typy.google.protobuf.internal import python_message
from typy.google.protobuf.internal import type_checkers
from typy.google.protobuf.descriptor import FieldDescriptor
from typy.google.protobuf import text_format
from Type import toType, FixedPoint, List, Dict, Instance
from Enum import MetaEnum

def setVariant(obj, value):
	if isinstance(value, bool):
		if hasattr(obj, 'Boolean'):
			obj.Boolean = value
		elif hasattr(obj, 'Integer'):
			obj.Integer = value
		elif hasattr(obj, 'Enum'):
			obj.Enum = value
		elif hasattr(obj, 'Double'):
			obj.Double = value
		elif hasattr(obj, 'Float'):
			obj.Float = value
		elif hasattr(obj, 'FixedPoint'):
			obj.FixedPoint = value
		else:
			raise TypeError
	elif isinstance(value, (int, long)):
		if hasattr(obj, 'Integer'):
			obj.Integer = value
		elif hasattr(obj, 'Enum'):
			obj.Enum = value
		elif hasattr(obj, 'Boolean'):
			obj.Boolean = value
		elif hasattr(obj, 'Double'):
			obj.Double = value
		elif hasattr(obj, 'Float'):
			obj.Float = value
		elif hasattr(obj, 'FixedPoint'):
			obj.FixedPoint = value
		else:
			raise TypeError
	elif isinstance(value, float):
		if hasattr(obj, 'Double'):
			obj.Double = value
		elif hasattr(obj, 'Float'):
			obj.Float = value
		elif hasattr(obj, 'FixedPoint'):
			obj.FixedPoint = value
		elif hasattr(obj, 'Integer'):
			obj.Integer = value
		elif hasattr(obj, 'Enum'):
			obj.Enum = value
		elif hasattr(obj, 'Boolean'):
			obj.Boolean = value
		else:
			raise TypeError
	elif isinstance(value, unicode):
		if hasattr(obj, 'String'):
			obj.String = value
		elif hasattr(obj, 'Bytes'):
			obj.Bytes = value
		else:
			raise TypeError
	elif isinstance(value, str):
		if hasattr(obj, 'Bytes'):
			obj.Bytes = value
		elif hasattr(obj, 'String'):
			obj.String = value
		else:
			raise TypeError
	elif hasattr(value, 'iteritems') and hasattr(obj, 'Dict'):
		obj.Dict = value
	elif hasattr(value, '__iter__') and hasattr(obj, 'List'):
		obj.List = value
	else:
		setattr(obj, value.__class__.__name__, value)


class PythonMessage(object):
	def __init__(self, obj):
		self.obj = obj
		self._is_present_in_parent = True

	def __str__(self):
		return str(self.obj)

	def IsInitialized(self):
		return True

	def MergeFrom(self, msg):
		if isinstance(msg, PythonMessage):
			self.obj = msg.obj
		else:
			self.obj = msg

	def ByteSize(self):
		return len(self.obj.Serialize())

	def _InternalSerialize(self, write):
		write(self.obj.Serialize())

	def _InternalParse(self, buffer, pos, new_pos):
		self.obj.Deserialize(buffer[pos: new_pos])
		return new_pos

class PythonDescriptor(object):
	def __init__(self, cls):
		self.name = cls.__name__
		self.full_name = '%s.%s' % (cls.__module__, cls.__name__)
		self._concrete_class = cls
		self.has_options = None
		self.oneofs = None

def _AddHasFieldMethod(message_descriptor, cls):
	from typy.google.protobuf import descriptor as descriptor_mod
	is_proto3 = (message_descriptor.syntax == "proto3")
	error_msg = python_message._Proto3HasError if is_proto3 else python_message._Proto2HasError

	hassable_fields = {}
	for field in message_descriptor.fields:
		# For proto3, only submessages and fields inside a oneof have presence.
		if (is_proto3 and field.cpp_type != FieldDescriptor.CPPTYPE_MESSAGE and
			not field.containing_oneof):
			continue
		hassable_fields[field.name] = field

	if not is_proto3:
		# Fields inside oneofs are never repeated (enforced by the compiler).
		for oneof in message_descriptor.oneofs:
			hassable_fields[oneof.name] = oneof

	def HasField(self, field_name):
		try:
			field = hassable_fields[field_name]
		except KeyError:
			raise ValueError(error_msg % field_name)

		if isinstance(field, descriptor_mod.OneofDescriptor):
			try:
				return HasField(self, self._oneofs[field].name)
			except KeyError:
				return False
		else:
			if field.cpp_type == FieldDescriptor.CPPTYPE_MESSAGE:
				value = self._fields.get(field)
				return value is not None and value._is_present_in_parent
			else:
				return field in self._fields

	cls.HasField = HasField
python_message._AddHasFieldMethod = _AddHasFieldMethod

Origin_DefaultValueConstructorForField = python_message._DefaultValueConstructorForField
def _DefaultValueConstructorForField(field):
	if isinstance(field.message_type, PythonDescriptor) and field.label != FieldDescriptor.LABEL_REPEATED:
		def MakePythonMessageDefault(message):
			return PythonMessage(field.message_type._concrete_class())
		return MakePythonMessageDefault
	else:
		return Origin_DefaultValueConstructorForField(field)
python_message._DefaultValueConstructorForField = _DefaultValueConstructorForField

Origin_PrintFieldValue = text_format._Printer.PrintFieldValue
def _PrintFieldValue(self, field, value):
	if isinstance(field.message_type, PythonDescriptor):
		self.out.write(str(value))
	else:
		Origin_PrintFieldValue(self, field, value)
text_format._Printer.PrintFieldValue = _PrintFieldValue

class BytesChecker(object):
	def DefaultValue(self):
		return b''

	def CheckValue(self, proposed_value):
		if not isinstance(proposed_value, (str, unicode)):
			message = ('%.1024r has type %s, but expected one of: %s' %
				(proposed_value, type(proposed_value), (str, unicode)))
			raise TypeError(message)
		return str(proposed_value)
type_checkers._VALUE_CHECKERS[FieldDescriptor.CPPTYPE_STRING] = BytesChecker()

def _AddListFieldsMethod(message_descriptor, cls):
	def ListFields(self):
		all_fields = [(k, v) for k, v in self._fields.iteritems() if python_message._IsPresent((k, v)) and k._sizer(v) > encoder._TagSize(k.number)]
		all_fields.sort(key = lambda item: item[0].number)
		return all_fields

	cls.ListFields = ListFields
python_message._AddListFieldsMethod = _AddListFieldsMethod


def _AddPropertiesForRepeatedField(field, cls):
	proto_field_name = field.name
	property_name = python_message._PropertyName(proto_field_name)

	def _get_default(self):
		field_value = self._fields.get(field)
		if field_value is None:
			field_value = field._default_constructor(self)
			field_value = self._fields.setdefault(field, field_value)
		return field_value

	def getter(self):
		return _get_default(self)
	getter.__module__ = None
	getter.__doc__ = 'Getter for %s.' % proto_field_name

	def setter(self, new_value):
		field_value = _get_default(self)
		if python_message._IsMapField(field):
			field_value._values = {}
			if not new_value:
				field_value._message_listener.Modified()
			else:
				for key in new_value:
					field_value[key] = new_value[key]
		else:
			field_value._values = []
			if not new_value:
				field_value._message_listener.Modified()
			else:
				for item in new_value:
					field_value.append(item)
		if field.containing_oneof:
			self._UpdateOneofState(field)

	doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
	setattr(cls, property_name, property(getter, setter, doc=doc))
python_message._AddPropertiesForRepeatedField = _AddPropertiesForRepeatedField

Origin_AddPropertiesForNonRepeatedScalarField = python_message._AddPropertiesForNonRepeatedScalarField
def _AddPropertiesForNonRepeatedScalarField(field, cls):
	if field.enum_type is None:
		return Origin_AddPropertiesForNonRepeatedScalarField(field, cls)
	proto_field_name = field.name
	property_name = python_message._PropertyName(proto_field_name)
	type_checker = type_checkers.GetTypeChecker(field)
	default_value = field.default_value
	is_proto3 = field.containing_type.syntax == "proto3"

	def getter(self):
		return MetaEnum.Enums[field.enum_type.name].__enum__[self._fields.get(field, default_value)]
	getter.__module__ = None
	getter.__doc__ = 'Getter for %s.' % proto_field_name

	clear_when_set_to_default = is_proto3 and not field.containing_oneof

	def field_setter(self, new_value):
		new_value = type_checker.CheckValue(new_value)
		if clear_when_set_to_default and not new_value:
			self._fields.pop(field, None)
		else:
			self._fields[field] = new_value
		if not self._cached_byte_size_dirty:
			self._Modified()

	if field.containing_oneof:
		def setter(self, new_value):
			field_setter(self, new_value)
			self._UpdateOneofState(field)
	else:
		setter = field_setter

	setter.__module__ = None
	setter.__doc__ = 'Setter for %s.' % proto_field_name

	doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
	setattr(cls, property_name, property(getter, setter, doc=doc))
python_message._AddPropertiesForNonRepeatedScalarField = _AddPropertiesForNonRepeatedScalarField

Origin_AddMergeFromMethod = python_message._AddMergeFromMethod
def _AddMergeFromMethod(cls):
	Origin_AddMergeFromMethod(cls)
	Origin_MergeFrom = cls.MergeFrom
	def MergeFrom(self, msg):
		if not isinstance(msg, cls) and cls.DESCRIPTOR.oneofs:
			return setVariant(self, msg)
		return Origin_MergeFrom(self, msg)
	cls.MergeFrom = MergeFrom
python_message._AddMergeFromMethod = _AddMergeFromMethod

def _AddPropertiesForNonRepeatedCompositeField(field, cls):
	proto_field_name = field.name
	property_name = python_message._PropertyName(proto_field_name)

	def getter(self):
		field_value = self._fields.get(field, None)
		if field_value is not None and field.message_type.oneofs:
			attr = field_value.WhichOneof('Variant')
			return None if attr is None else getattr(field_value, attr)
		if field_value is None:
			field_value = field._default_constructor(self)
			field_value = self._fields.setdefault(field, field_value)
		if isinstance(field.message_type, PythonDescriptor):
			return field_value.obj
		return field_value
	getter.__module__ = None
	getter.__doc__ = 'Getter for %s.' % proto_field_name

	def setter(self, value):
		if value is None:
			self._fields.pop(field, None)
			self._Modified()
		else:
			if field.message_type.oneofs:
				field_value = self._fields.get(field)
				if field_value is None:
					field_value = field._default_constructor(self)
					field_value = self._fields.setdefault(field, field_value)
				return setVariant(field_value, value)
			if isinstance(field.message_type, PythonDescriptor):
				value = PythonMessage(value)
			self._fields[field] = value
			self._Modified()
			value._is_present_in_parent = True
			if field.containing_oneof:
				self._UpdateOneofState(field)

	doc = 'Magic attribute generated for "%s" proto field.' % proto_field_name
	setattr(cls, property_name, property(getter, setter, doc=doc))
python_message._AddPropertiesForNonRepeatedCompositeField = _AddPropertiesForNonRepeatedCompositeField

from typy.google.protobuf.internal import containers

Origin_GetInitializeDefaultForMap = python_message._GetInitializeDefaultForMap
def _GetInitializeDefaultForMap(field):
	MakeMapDefault = Origin_GetInitializeDefaultForMap(field)
	value_type = field.message_type.fields_by_name['value']
	if value_type.label == FieldDescriptor.LABEL_REPEATED:
		if value_type.cpp_type == FieldDescriptor.CPPTYPE_MESSAGE:
			if value_type.message_type.has_options and value_type.message_type.GetOptions().map_entry:
				def MakeDictMapDefault(message):
					_map = MakeMapDefault(message)
					_map._nestingDict = lambda: value_type._default_constructor(message)
					return _map
				return MakeDictMapDefault
			else:
				def MakeListMapDefault(message):
					_map = MakeMapDefault(message)
					_map._nestingList = lambda: value_type._default_constructor(message)
					return _map
				return MakeListMapDefault
		else:
			def MakeListMapDefault(message):
				_map = MakeMapDefault(message)
				_map._nestingList = True
				return _map
			return MakeListMapDefault
	else:
		return MakeMapDefault
python_message._GetInitializeDefaultForMap = _GetInitializeDefaultForMap

class _ScalarMap(containers.ScalarMap):
	__slots__ = '_nestingList'
	_is_present_in_parent = True

	def __getitem__(self, key):
		if getattr(self, '_nestingList', None):
			return self._values[key]
		return super(_ScalarMap, self).__getitem__(key)

	def __setitem__(self, key, value):
		if getattr(self, '_nestingList', None):
			checked_key = self._key_checker.CheckValue(key)
			checked_value = [self._value_checker.CheckValue(v) for v in value]
			self._values[checked_key] = checked_value
			self._message_listener.Modified()
		else:
			super(_ScalarMap, self).__setitem__(key, value)
containers.ScalarMap = _ScalarMap

class _MessageMap(containers.MessageMap):
	__slots__ = '_nestingList', '_nestingDict'
	_is_present_in_parent = True

	def __getitem__(self, key):
		nesting = getattr(self, '_nestingList', None) or getattr(self, '_nestingDict', None)
		if nesting:
			try:
				return self._values[key]
			except KeyError:
				key = self._key_checker.CheckValue(key)
				new_element = nesting()
				self._values[key] = new_element
				self._message_listener.Modified()
				return new_element
		elif self._message_descriptor.oneofs:
			if key not in self._values:
				return None
			value = self._values[key]
			attr = value.WhichOneof('Variant')
			return None if attr is None else getattr(value, attr)
		elif isinstance(self._message_descriptor, PythonDescriptor):
			try:
				return self._values[key].obj
			except KeyError:
				key = self._key_checker.CheckValue(key)
				new_element = PythonMessage(self._message_descriptor._concrete_class())
				self._values[key] = new_element
				self._message_listener.Modified()
				return new_element.obj
		return super(_MessageMap, self).__getitem__(key)

	def __setitem__(self, key, value):
		if getattr(self, '_nestingList', None):
			field_value = self.__getitem__(key)
			field_value._values = []
			return field_value.extend(value)
		elif getattr(self, '_nestingDict', None):
			field_value = self.__getitem__(key)
			field_value._values = {}
			for k, v in value.iteritems():
				field_value[k] = v
			return
		elif self._message_descriptor.oneofs:
			variant = super(_MessageMap, self).__getitem__(key)
			return setVariant(variant, value)

		if isinstance(self._message_descriptor, PythonDescriptor):
			value = PythonMessage(value)
		self._values[key] = value
		self._message_listener.Modified()
		value._is_present_in_parent = True

	def MergeFrom(self, other):
		for key in other:
			self[key] = other[key]

containers.MessageMap = _MessageMap

class _RepeatedScalarFieldContainer(containers.RepeatedScalarFieldContainer):
	_is_present_in_parent = True

	def __init__(self, message_listener, type_checker):
		containers.BaseContainer.__init__(self, message_listener)
		self._type_checker = type_checker

	def __iter__(self):
		return iter(self._values)
containers.RepeatedScalarFieldContainer = _RepeatedScalarFieldContainer

class _RepeatedCompositeFieldContainer(containers.RepeatedCompositeFieldContainer):
	_is_present_in_parent = True

	def __init__(self, message_listener, message_descriptor):
		containers.BaseContainer.__init__(self, message_listener)
		self._message_descriptor = message_descriptor

	def __getitem__(self, key):
		if self._message_descriptor.oneofs:
			value = self._values[key]
			attr = value.WhichOneof('Variant')
			return None if attr is None else getattr(value, attr)
		elif isinstance(self._message_descriptor, PythonDescriptor):
			return self._values[key].obj
		return super(_RepeatedCompositeFieldContainer, self).__getitem__(key)

	def __iter__(self):
		if self._message_descriptor.oneofs:
			return iter([getattr(v, v.WhichOneof('Variant'), None) for v in self._values])
		return iter(self._values)

	def add(self, **kwargs):
		if isinstance(self._message_descriptor, PythonDescriptor):
			new_element = PythonMessage(self._message_descriptor._concrete_class(**kwargs))
			self._values.append(new_element)
			if not self._message_listener.dirty:
				self._message_listener.Modified()
			return new_element
		return super(_RepeatedCompositeFieldContainer, self).add(**kwargs)

	def append(self, item):
		if self._message_descriptor.oneofs:
			return setVariant(self.add(), item)

		if isinstance(self._message_descriptor, PythonDescriptor):
			item = PythonMessage(item)
		self._values.append(item)
		if not self._message_listener.dirty:
			self._message_listener.Modified()
		item._is_present_in_parent = True
containers.RepeatedCompositeFieldContainer = _RepeatedCompositeFieldContainer

from typy.google.protobuf.internal import decoder
from typy.google.protobuf.internal import encoder
from typy.google.protobuf.internal import wire_format
Origin_MapDecoder = decoder.MapDecoder
def _MapDecoder(field_descriptor, new_default, is_message_map):
	Origin_DecodeMap = Origin_MapDecoder(field_descriptor, new_default, is_message_map)
	if not is_message_map:
		return Origin_DecodeMap
	key = field_descriptor
	tag_bytes = encoder.TagBytes(field_descriptor.number, wire_format.WIRETYPE_LENGTH_DELIMITED)
	tag_len = len(tag_bytes)
	local_DecodeVarint = decoder._DecodeVarint
	message_type = field_descriptor.message_type
	def _DecodeMap(buffer, pos, end, message, field_dict):
		submsg = message_type._concrete_class()
		value = field_dict.get(key)
		if value is None:
			value = field_dict.setdefault(key, new_default(message))
		while 1:
			(size, pos) = local_DecodeVarint(buffer, pos)
			new_pos = pos + size
			if new_pos > end:
				raise decoder._DecodeError('Truncated message.')
			submsg.Clear()
			if submsg._InternalParse(buffer, pos, new_pos) != new_pos:
				raise decoder._DecodeError('Unexpected end-group tag.')

			if getattr(value, '_nestingList', None) or getattr(value, '_nestingDict', None):
				value.__getitem__(submsg.key).MergeFrom(submsg.value)
			elif isinstance(value._message_descriptor, PythonDescriptor):
				value.__setitem__(submsg.key, submsg.value)
			else:
				super(_MessageMap, value).__getitem__(submsg.key).MergeFrom(submsg.value)
			pos = new_pos + tag_len
			if buffer[new_pos:pos] != tag_bytes or new_pos == end:
				return new_pos
	return _DecodeMap
decoder.MapDecoder = _MapDecoder

Origin_MessageSizer = encoder.MessageSizer
def _MessageSizer(field_number, is_repeated, is_packed):
	if is_repeated:
		tag_size = encoder._TagSize(field_number)
		def RepeatedFieldSize(value):
			result = tag_size * len(value)
			if value._message_descriptor.oneofs:
				value = value._values
			for element in value:
				l = element.ByteSize()
				result += encoder._VarintSize(l) + l
			return result
		return RepeatedFieldSize
	else:
		return Origin_MessageSizer(field_number, is_repeated, is_packed)
encoder.MessageSizer = _MessageSizer
type_checkers.TYPE_TO_SIZER[FieldDescriptor.TYPE_MESSAGE] = _MessageSizer

Origin_MessageEncoder = encoder.MessageEncoder
def _MessageEncoder(field_number, is_repeated, is_packed):
	if is_repeated:
		tag = encoder.TagBytes(field_number, wire_format.WIRETYPE_LENGTH_DELIMITED)
		def EncodeRepeatedField(write, value):
			if value._message_descriptor.oneofs:
				value = value._values
			for element in value:
				write(tag)
				encoder._EncodeVarint(write, element.ByteSize())
				element._InternalSerialize(write)
		return EncodeRepeatedField
	else:
		return Origin_MessageEncoder(field_number, is_repeated, is_packed)
encoder.MessageEncoder = _MessageEncoder
type_checkers.TYPE_TO_ENCODER[FieldDescriptor.TYPE_MESSAGE] = _MessageEncoder


def FixedPointSizer(sizer, precision, floor, includeZero):
	precision = 10 ** precision
	floor = floor * precision
	def _FixedPointSizer(value):
		value = int(value * precision)
		return sizer(value - floor) if includeZero or value != 0 else 0
	return _FixedPointSizer

def EncodeFixedPoint(encoder, precision, floor, includeZero):
	precision = 10 ** precision
	floor = floor * precision
	def _EncodeFixedPoint(write, value):
		value = int(value * precision)
		if includeZero or value != 0:
			return encoder(write, value - floor)
	return _EncodeFixedPoint

def DecodeFixedPoint(decoder, precision, floor):
	precision = 10 ** precision
	def _DecodeFixedPoint(buffer, pos):
		(element, new_pos) = decoder(buffer, pos)
		return float(element) / precision + floor, new_pos
	return _DecodeFixedPoint


def _AttachFixedPointHelpers(cls, field, precision, floor):
	is_repeated = (field.label == FieldDescriptor.LABEL_REPEATED)
	is_packed = (is_repeated and wire_format.IsTypePackable(FieldDescriptor.TYPE_INT32))
	sizer = FixedPointSizer(encoder._SignedVarintSize, precision, floor, is_repeated)
	field._encoder = encoder._SimpleEncoder(wire_format.WIRETYPE_VARINT, EncodeFixedPoint(encoder._EncodeSignedVarint, precision, floor, is_repeated), sizer)(field.number, is_repeated, is_packed)
	field._sizer = encoder._SimpleSizer(sizer)(field.number, is_repeated, is_packed)
	oneof_descriptor = None if field.containing_oneof is None else field
	tag_bytes = encoder.TagBytes(field.number, type_checkers.FIELD_TYPE_TO_WIRE_TYPE[FieldDescriptor.TYPE_INT32])
	field_decoder = decoder._SimpleDecoder(wire_format.WIRETYPE_VARINT, DecodeFixedPoint(decoder._DecodeSignedVarint32, precision, floor))(field.number, is_repeated, is_packed, field, field._default_constructor)
	cls._decoders_by_tag[tag_bytes] = (field_decoder, oneof_descriptor)
	if is_packed:
		tag_bytes = encoder.TagBytes(field.number, wire_format.WIRETYPE_LENGTH_DELIMITED)
		cls._decoders_by_tag[tag_bytes] = (field_decoder, oneof_descriptor)


def initObjectClass(cls, clsname, bases, attrs):
	cls.IsInitialized = lambda s, *args, **kwargs: True
	descriptor = attrs[python_message.GeneratedProtocolMessageType._DESCRIPTOR_KEY]
	for field in descriptor.fields:
		p = cls.____properties__[field.name]
		if isinstance(p, FixedPoint):
			_AttachFixedPointHelpers(cls, field, p.precision, p.floor)
		elif isinstance(p, List) and isinstance(p.elementType, FixedPoint):
			_AttachFixedPointHelpers(cls, field, p.elementType.precision, p.elementType.floor)
		elif isinstance(p, Dict) and isinstance(p.valueType, FixedPoint):
			_AttachFixedPointHelpers(attrs[field.message_type.name], field.message_type.fields_by_name['value'], p.valueType.precision, p.valueType.floor)
		elif isinstance(p, Instance) and len(p.pyType) > 1:
			for vp in p.pyType:
				if vp is None: continue
				vp = toType(vp)
				if isinstance(vp, FixedPoint):
					_AttachFixedPointHelpers(attrs[field.message_type.name], field.message_type.fields_by_name['FixedPoint'], vp.precision, vp.floor)
		elif isinstance(p, List) and isinstance(p.elementType, Instance) and len(p.elementType.pyType) > 1:
			for vp in p.elementType.pyType:
				if vp is None: continue
				vp = toType(vp)
				if isinstance(vp, FixedPoint):
					_AttachFixedPointHelpers(attrs[field.message_type.name], field.message_type.fields_by_name['FixedPoint'], vp.precision, vp.floor)
		elif isinstance(p, Dict) and isinstance(p.valueType, Instance) and len(p.valueType.pyType) > 1:
			for vp in p.valueType.pyType:
				if vp is None: continue
				vp = toType(vp)
				if isinstance(vp, FixedPoint):
					_AttachFixedPointHelpers(attrs[field.message_type.fields_by_name['value'].message_type.name], field.message_type.fields_by_name['value'].message_type.fields_by_name['FixedPoint'], vp.precision, vp.floor)
