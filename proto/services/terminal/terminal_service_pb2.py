# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/services/terminal/terminal_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n.proto/services/terminal/terminal_service.proto\x12\x08terminal\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\xa9\x01\n\x07Results\x12\x15\n\rwellness_data\x18\x01 \x01(\x02\x12\x36\n\x12wellness_timestamp\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x16\n\x0epollution_data\x18\x03 \x01(\x02\x12\x37\n\x13pollution_timestamp\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp2K\n\x0fTerminalService\x12\x38\n\x0bSendResults\x12\x11.terminal.Results\x1a\x16.google.protobuf.Emptyb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.services.terminal.terminal_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _RESULTS._serialized_start=123
  _RESULTS._serialized_end=292
  _TERMINALSERVICE._serialized_start=294
  _TERMINALSERVICE._serialized_end=369
# @@protoc_insertion_point(module_scope)
