# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/cloud/app_device_info.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import version_pb2 as proto_dot_cloud_dot_version__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!proto/cloud/app_device_info.proto\x12\x0bproto.cloud\x1a\x19proto/cloud/version.proto\"\xd9\x02\n\x07\x41ppInfo\x12/\n\x08platform\x18\x01 \x01(\x0e\x32\x1d.proto.cloud.AppInfo.Platform\x12\x13\n\x0b\x61pp_version\x18\x02 \x01(\t\x12\x11\n\tfamily_id\x18\x03 \x01(\t\x12\x0f\n\x07user_id\x18\x04 \x01(\t\x12\x34\n\x0b\x64\x61ta_center\x18\x05 \x01(\x0e\x32\x1f.proto.cloud.AppInfo.DataCenter\x12.\n\x0c\x61pp_function\x18\x06 \x01(\x0b\x32\x18.proto.cloud.AppFunction\x12\x14\n\x0ctime_zone_id\x18\x07 \x01(\t\"B\n\x08Platform\x12\x0c\n\x08PF_OTHER\x10\x00\x12\x0e\n\nPF_ANDROID\x10\x01\x12\n\n\x06PF_IOS\x10\x02\x12\x0c\n\x08PF_CLOUD\x10\x03\"$\n\nDataCenter\x12\x06\n\x02\x45U\x10\x00\x12\x06\n\x02\x41Z\x10\x01\x12\x06\n\x02\x41Y\x10\x02\"\xb3\x02\n\nDeviceInfo\x12\x14\n\x0cproduct_name\x18\x01 \x01(\t\x12\x10\n\x08video_sn\x18\x02 \x01(\t\x12\x12\n\ndevice_mac\x18\x03 \x01(\t\x12\x10\n\x08software\x18\x04 \x01(\t\x12\x10\n\x08hardware\x18\x05 \x01(\r\x12\x11\n\twifi_name\x18\x06 \x01(\t\x12\x0f\n\x07wifi_ip\x18\x07 \x01(\t\x12\x14\n\x0clast_user_id\x18\x08 \x01(\t\x12\x30\n\x07station\x18\x0b \x01(\x0b\x32\x1f.proto.cloud.DeviceInfo.Station\x12*\n\nproto_info\x18\x0c \x01(\x0b\x32\x16.proto.cloud.ProtoInfo\x1a-\n\x07Station\x12\x10\n\x08software\x18\x01 \x01(\t\x12\x10\n\x08hardware\x18\x02 \x01(\rb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.cloud.app_device_info_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_APPINFO']._serialized_start=78
  _globals['_APPINFO']._serialized_end=423
  _globals['_APPINFO_PLATFORM']._serialized_start=319
  _globals['_APPINFO_PLATFORM']._serialized_end=385
  _globals['_APPINFO_DATACENTER']._serialized_start=387
  _globals['_APPINFO_DATACENTER']._serialized_end=423
  _globals['_DEVICEINFO']._serialized_start=426
  _globals['_DEVICEINFO']._serialized_end=733
  _globals['_DEVICEINFO_STATION']._serialized_start=688
  _globals['_DEVICEINFO_STATION']._serialized_end=733
# @@protoc_insertion_point(module_scope)