# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/cloud/clean_statistics.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\"proto/cloud/clean_statistics.proto\x12\x0bproto.cloud\"\xb1\x02\n\x0f\x43leanStatistics\x12\x33\n\x06single\x18\x01 \x01(\x0b\x32#.proto.cloud.CleanStatistics.Single\x12\x31\n\x05total\x18\x02 \x01(\x0b\x32\".proto.cloud.CleanStatistics.Total\x12\x36\n\nuser_total\x18\x03 \x01(\x0b\x32\".proto.cloud.CleanStatistics.Total\x1a\x34\n\x06Single\x12\x16\n\x0e\x63lean_duration\x18\x01 \x01(\r\x12\x12\n\nclean_area\x18\x02 \x01(\r\x1aH\n\x05Total\x12\x16\n\x0e\x63lean_duration\x18\x01 \x01(\r\x12\x12\n\nclean_area\x18\x02 \x01(\r\x12\x13\n\x0b\x63lean_count\x18\x03 \x01(\rb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.cloud.clean_statistics_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_CLEANSTATISTICS']._serialized_start=52
  _globals['_CLEANSTATISTICS']._serialized_end=357
  _globals['_CLEANSTATISTICS_SINGLE']._serialized_start=231
  _globals['_CLEANSTATISTICS_SINGLE']._serialized_end=283
  _globals['_CLEANSTATISTICS_TOTAL']._serialized_start=285
  _globals['_CLEANSTATISTICS_TOTAL']._serialized_end=357
# @@protoc_insertion_point(module_scope)