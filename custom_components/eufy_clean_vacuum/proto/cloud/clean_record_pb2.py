# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/cloud/clean_record.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import clean_param_pb2 as proto_dot_cloud_dot_clean__param__pb2
from . import stream_pb2 as proto_dot_cloud_dot_stream__pb2
from . import p2pdata_pb2 as proto_dot_cloud_dot_p2pdata__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eproto/cloud/clean_record.proto\x12\x0bproto.cloud\x1a\x1dproto/cloud/clean_param.proto\x1a\x18proto/cloud/stream.proto\x1a\x19proto/cloud/p2pdata.proto\"\xaa\x04\n\x0f\x43leanRecordDesc\x12\x12\n\nstart_time\x18\x01 \x01(\x04\x12\x10\n\x08\x65nd_time\x18\x02 \x01(\x04\x12\x10\n\x08\x64uration\x18\x03 \x01(\r\x12\x0c\n\x04\x61rea\x18\x04 \x01(\r\x12*\n\nclean_type\x18\x05 \x01(\x0b\x32\x16.proto.cloud.CleanType\x12@\n\rfinish_reason\x18\x06 \x01(\x0e\x32).proto.cloud.CleanRecordDesc.FinishReason\x12\x31\n\x05\x65xtra\x18\x07 \x01(\x0b\x32\".proto.cloud.CleanRecordDesc.Extra\x1a\xe5\x01\n\x05\x45xtra\x12\x35\n\x04mode\x18\x01 \x01(\x0e\x32\'.proto.cloud.CleanRecordDesc.Extra.Mode\x12\x0b\n\x03mus\x18\x02 \x01(\r\x12\x12\n\nerror_code\x18\x03 \x01(\r\x12\x13\n\x0bprompt_code\x18\x04 \x01(\r\"o\n\x04Mode\x12\x08\n\x04\x41UTO\x10\x00\x12\x0f\n\x0bSELECT_ROOM\x10\x01\x12\x0f\n\x0bSELECT_ZONE\x10\x02\x12\x08\n\x04SPOT\x10\x03\x12\x17\n\x13SCHEDULE_AUTO_CLEAN\x10\x04\x12\x18\n\x14SCHEDULE_ROOMS_CLEAN\x10\x05\"H\n\x0c\x46inishReason\x12\r\n\tCOMPLETED\x10\x00\x12\x0b\n\x07MANUDAL\x10\x01\x12\r\n\tLOW_POWER\x10\x02\x12\r\n\tEXCEPTION\x10\x03\"\xba\x04\n\x0f\x43leanRecordData\x12;\n\x0frestricted_zone\x18\x01 \x01(\x0b\x32\".proto.cloud.stream.RestrictedZone\x12\x34\n\ttemp_data\x18\x02 \x01(\x0b\x32!.proto.cloud.stream.TemporaryData\x12\x33\n\x0broom_params\x18\x03 \x01(\x0b\x32\x1e.proto.cloud.stream.RoomParams\x12\x11\n\tpath_data\x18\x06 \x01(\x0c\x12$\n\x03map\x18\n \x01(\x0b\x32\x17.proto.cloud.stream.Map\x12\x35\n\x0croom_outline\x18\x0b \x01(\x0b\x32\x1f.proto.cloud.stream.RoomOutline\x12\x37\n\robstacle_info\x18\x0c \x01(\x0b\x32 .proto.cloud.stream.ObstacleInfo\x12;\n\x0cpath_data_v2\x18\r \x01(\x0b\x32%.proto.cloud.CleanRecordData.PathData\x12-\n\x07map_p2p\x18\x14 \x01(\x0b\x32\x1c.proto.cloud.p2p.CompleteMap\x12/\n\x08path_p2p\x18\x15 \x01(\x0b\x32\x1d.proto.cloud.p2p.CompletePath\x1a\x39\n\x08PathData\x12-\n\x06points\x18\x01 \x03(\x0b\x32\x1d.proto.cloud.stream.PathPoint\"\xa1\x03\n\x10\x43ruiseRecordDesc\x12\x12\n\nstart_time\x18\x01 \x01(\x04\x12\x10\n\x08\x65nd_time\x18\x02 \x01(\x04\x12\x10\n\x08\x64uration\x18\x03 \x01(\r\x12\x41\n\rfinish_reason\x18\x04 \x01(\x0e\x32*.proto.cloud.CruiseRecordDesc.FinishReason\x12\x32\n\x05\x65xtra\x18\x07 \x01(\x0b\x32#.proto.cloud.CruiseRecordDesc.Extra\x1a\x93\x01\n\x05\x45xtra\x12\x36\n\x04mode\x18\x01 \x01(\x0e\x32(.proto.cloud.CruiseRecordDesc.Extra.Mode\"R\n\x04Mode\x12\x11\n\rGLOBAL_CRUISE\x10\x00\x12\x10\n\x0cPOINT_CRUISE\x10\x01\x12\x10\n\x0cZONES_CRUISE\x10\x02\x12\x13\n\x0fSCHEDULE_CRUISE\x10\x03\"H\n\x0c\x46inishReason\x12\r\n\tCOMPLETED\x10\x00\x12\x0b\n\x07MANUDAL\x10\x01\x12\r\n\tLOW_POWER\x10\x02\x12\r\n\tEXCEPTION\x10\x03\"\xf8\x03\n\x10\x43ruiseRecordData\x12;\n\x0frestricted_zone\x18\x01 \x01(\x0b\x32\".proto.cloud.stream.RestrictedZone\x12\x34\n\ttemp_data\x18\x02 \x01(\x0b\x32!.proto.cloud.stream.TemporaryData\x12\x33\n\x0broom_params\x18\x03 \x01(\x0b\x32\x1e.proto.cloud.stream.RoomParams\x12\x37\n\robstacle_info\x18\x04 \x01(\x0b\x32 .proto.cloud.stream.ObstacleInfo\x12\x11\n\tpath_data\x18\x05 \x01(\x0c\x12\x33\n\x0b\x63ruise_data\x18\x06 \x01(\x0b\x32\x1e.proto.cloud.stream.CruiseData\x12$\n\x03map\x18\x07 \x01(\x0b\x32\x17.proto.cloud.stream.Map\x12\x35\n\x0croom_outline\x18\x08 \x01(\x0b\x32\x1f.proto.cloud.stream.RoomOutline\x12-\n\x07map_p2p\x18\x14 \x01(\x0b\x32\x1c.proto.cloud.p2p.CompleteMap\x12/\n\x08path_p2p\x18\x15 \x01(\x0b\x32\x1d.proto.cloud.p2p.CompletePathb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.cloud.clean_record_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_CLEANRECORDDESC']._serialized_start=132
  _globals['_CLEANRECORDDESC']._serialized_end=686
  _globals['_CLEANRECORDDESC_EXTRA']._serialized_start=383
  _globals['_CLEANRECORDDESC_EXTRA']._serialized_end=612
  _globals['_CLEANRECORDDESC_EXTRA_MODE']._serialized_start=501
  _globals['_CLEANRECORDDESC_EXTRA_MODE']._serialized_end=612
  _globals['_CLEANRECORDDESC_FINISHREASON']._serialized_start=614
  _globals['_CLEANRECORDDESC_FINISHREASON']._serialized_end=686
  _globals['_CLEANRECORDDATA']._serialized_start=689
  _globals['_CLEANRECORDDATA']._serialized_end=1259
  _globals['_CLEANRECORDDATA_PATHDATA']._serialized_start=1202
  _globals['_CLEANRECORDDATA_PATHDATA']._serialized_end=1259
  _globals['_CRUISERECORDDESC']._serialized_start=1262
  _globals['_CRUISERECORDDESC']._serialized_end=1679
  _globals['_CRUISERECORDDESC_EXTRA']._serialized_start=1458
  _globals['_CRUISERECORDDESC_EXTRA']._serialized_end=1605
  _globals['_CRUISERECORDDESC_EXTRA_MODE']._serialized_start=1523
  _globals['_CRUISERECORDDESC_EXTRA_MODE']._serialized_end=1605
  _globals['_CRUISERECORDDESC_FINISHREASON']._serialized_start=614
  _globals['_CRUISERECORDDESC_FINISHREASON']._serialized_end=686
  _globals['_CRUISERECORDDATA']._serialized_start=1682
  _globals['_CRUISERECORDDATA']._serialized_end=2186
# @@protoc_insertion_point(module_scope)