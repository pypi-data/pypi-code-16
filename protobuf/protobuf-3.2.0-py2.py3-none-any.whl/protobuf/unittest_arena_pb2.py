# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google/protobuf/unittest_arena.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import unittest_no_arena_import_pb2 as google_dot_protobuf_dot_unittest__no__arena__import__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='google/protobuf/unittest_arena.proto',
  package='proto2_arena_unittest',
  syntax='proto2',
  serialized_pb=_b('\n$google/protobuf/unittest_arena.proto\x12\x15proto2_arena_unittest\x1a.google/protobuf/unittest_no_arena_import.proto\"\x1a\n\rNestedMessage\x12\t\n\x01\x64\x18\x01 \x01(\x05\"\xb2\x01\n\x0c\x41renaMessage\x12\x45\n\x17repeated_nested_message\x18\x01 \x03(\x0b\x32$.proto2_arena_unittest.NestedMessage\x12[\n repeated_import_no_arena_message\x18\x02 \x03(\x0b\x32\x31.proto2_arena_unittest.ImportNoArenaNestedMessageB\x03\xf8\x01\x01')
  ,
  dependencies=[google_dot_protobuf_dot_unittest__no__arena__import__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_NESTEDMESSAGE = _descriptor.Descriptor(
  name='NestedMessage',
  full_name='proto2_arena_unittest.NestedMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='d', full_name='proto2_arena_unittest.NestedMessage.d', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=111,
  serialized_end=137,
)


_ARENAMESSAGE = _descriptor.Descriptor(
  name='ArenaMessage',
  full_name='proto2_arena_unittest.ArenaMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='repeated_nested_message', full_name='proto2_arena_unittest.ArenaMessage.repeated_nested_message', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='repeated_import_no_arena_message', full_name='proto2_arena_unittest.ArenaMessage.repeated_import_no_arena_message', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=140,
  serialized_end=318,
)

_ARENAMESSAGE.fields_by_name['repeated_nested_message'].message_type = _NESTEDMESSAGE
_ARENAMESSAGE.fields_by_name['repeated_import_no_arena_message'].message_type = google_dot_protobuf_dot_unittest__no__arena__import__pb2._IMPORTNOARENANESTEDMESSAGE
DESCRIPTOR.message_types_by_name['NestedMessage'] = _NESTEDMESSAGE
DESCRIPTOR.message_types_by_name['ArenaMessage'] = _ARENAMESSAGE

NestedMessage = _reflection.GeneratedProtocolMessageType('NestedMessage', (_message.Message,), dict(
  DESCRIPTOR = _NESTEDMESSAGE,
  __module__ = 'google.protobuf.unittest_arena_pb2'
  # @@protoc_insertion_point(class_scope:proto2_arena_unittest.NestedMessage)
  ))
_sym_db.RegisterMessage(NestedMessage)

ArenaMessage = _reflection.GeneratedProtocolMessageType('ArenaMessage', (_message.Message,), dict(
  DESCRIPTOR = _ARENAMESSAGE,
  __module__ = 'google.protobuf.unittest_arena_pb2'
  # @@protoc_insertion_point(class_scope:proto2_arena_unittest.ArenaMessage)
  ))
_sym_db.RegisterMessage(ArenaMessage)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\370\001\001'))
# @@protoc_insertion_point(module_scope)
