# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/cloud/stream_wrap.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import stream_pb2 as proto_dot_cloud_dot_stream__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dproto/cloud/stream_wrap.proto\x12\x12proto.cloud.stream\x1a\x18proto/cloud/stream.proto\"E\n\x0eRoomParamsWrap\x12\x33\n\x0broom_params\x18\x01 \x03(\x0b\x32\x1e.proto.cloud.stream.RoomParams\"K\n\x10ObstacleInfoWrap\x12\x37\n\robstacle_info\x18\x01 \x03(\x0b\x32 .proto.cloud.stream.ObstacleInfob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.cloud.stream_wrap_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_ROOMPARAMSWRAP']._serialized_start=79
  _globals['_ROOMPARAMSWRAP']._serialized_end=148
  _globals['_OBSTACLEINFOWRAP']._serialized_start=150
  _globals['_OBSTACLEINFOWRAP']._serialized_end=225
# @@protoc_insertion_point(module_scope)