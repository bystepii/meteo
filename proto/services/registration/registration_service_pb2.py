# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/services/registration/registration_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n6proto/services/registration/registration_service.proto\x12\x0cregistration\x1a\x1bgoogle/protobuf/empty.proto\"=\n\x0fRegisterRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\r\"\x12\n\x03UID\x12\x0b\n\x03uid\x18\x01 \x01(\t\":\n\x10RegisterResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rerror_message\x18\x02 \x01(\t2\x9d\x01\n\x13RegistrationService\x12K\n\x08Register\x12\x1d.registration.RegisterRequest\x1a\x1e.registration.RegisterResponse\"\x00\x12\x39\n\nUnregister\x12\x11.registration.UID\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.services.registration.registration_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGISTERREQUEST._serialized_start=101
  _REGISTERREQUEST._serialized_end=162
  _UID._serialized_start=164
  _UID._serialized_end=182
  _REGISTERRESPONSE._serialized_start=184
  _REGISTERRESPONSE._serialized_end=242
  _REGISTRATIONSERVICE._serialized_start=245
  _REGISTRATIONSERVICE._serialized_end=402
# @@protoc_insertion_point(module_scope)
