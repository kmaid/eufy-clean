# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/cloud/error_code_list_t2265.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'proto/cloud/error_code_list_t2265.proto\x12\x11proto.cloud.t22xx*\xbc\x0e\n\rErrorCodeList\x12\x0e\n\nE0000_NONE\x10\x00\x12\"\n\x1d\x45\x31\x30\x31\x30_LEFT_WHEEL_OPEN_CIRCUIT\x10\xf2\x07\x12#\n\x1e\x45\x31\x30\x31\x31_LEFT_WHEEL_SHORT_CIRCUIT\x10\xf3\x07\x12\x1b\n\x16\x45\x31\x30\x31\x32_LEFT_WHEEL_ERROR\x10\xf4\x07\x12\x1b\n\x16\x45\x31\x30\x31\x33_LEFT_WHEEL_STUCK\x10\xf5\x07\x12#\n\x1e\x45\x31\x30\x32\x30_RIGHT_WHEEL_OPEN_CIRCUIT\x10\xfc\x07\x12$\n\x1f\x45\x31\x30\x32\x31_RIGHT_WHEEL_SHORT_CIRCUIT\x10\xfd\x07\x12\x1c\n\x17\x45\x31\x30\x32\x32_RIGHT_WHEEL_ERROR\x10\xfe\x07\x12\x1c\n\x17\x45\x31\x30\x32\x33_RIGHT_WHEEL_STUCK\x10\xff\x07\x12\x1e\n\x19\x45\x31\x30\x33\x30_WHEELS_OPEN_CIRCUIT\x10\x86\x08\x12\x1f\n\x1a\x45\x31\x30\x33\x31_WHEELS_SHORT_CIRCUIT\x10\x87\x08\x12\x17\n\x12\x45\x31\x30\x33\x32_WHEELS_ERROR\x10\x88\x08\x12\x17\n\x12\x45\x31\x30\x33\x33_WHEELS_STUCK\x10\x89\x08\x12$\n\x1f\x45\x32\x30\x31\x30_SUNCTION_FAN_OPEN_CIRCUIT\x10\xda\x0f\x12!\n\x1c\x45\x32\x30\x31\x33_SUNCTION_FAN_RPM_ERROR\x10\xdd\x0f\x12$\n\x1f\x45\x32\x31\x31\x30_ROLLER_BRUSH_OPEN_CIRCUIT\x10\xbe\x10\x12%\n E2111_ROLLER_BRUSH_SHORT_CIRCUIT\x10\xbf\x10\x12\x1d\n\x18\x45\x32\x31\x31\x32_ROLLER_BRUSH_STUCK\x10\xc0\x10\x12\"\n\x1d\x45\x32\x32\x31\x30_SIDE_BRUSH_OPEN_CIRCUIT\x10\xa2\x11\x12#\n\x1e\x45\x32\x32\x31\x31_SIDE_BRUSH_SHORT_CIRCUIT\x10\xa3\x11\x12\x1b\n\x16\x45\x32\x32\x31\x32_SIDE_BRUSH_ERROR\x10\xa4\x11\x12\x1b\n\x16\x45\x32\x32\x31\x33_SIDE_BRUSH_STUCK\x10\xa5\x11\x12 \n\x1b\x45\x32\x33\x31\x30_DUSTBIN_NOT_INSTALLED\x10\x86\x12\x12+\n&E2311_DUSTBIN_NOT_CLEANED_FOR_TOO_LONG\x10\x87\x12\x12(\n#E3010_ROBOT_WATER_PUMP_OPEN_CIRCUIT\x10\xc2\x17\x12#\n\x1e\x45\x33\x30\x31\x33_ROBOT_WATER_INSUFFICIENT\x10\xc5\x17\x12\x16\n\x11\x45\x34\x30\x31\x30_LASER_ERROR\x10\xaa\x1f\x12\x18\n\x13\x45\x34\x30\x31\x31_LASER_BLOCKED\x10\xab\x1f\x12\x16\n\x11\x45\x34\x30\x31\x32_LASER_STUCK\x10\xac\x1f\x12\x1c\n\x17\x45\x34\x31\x31\x31_LEFT_BUMPER_STUCK\x10\x8f \x12\x1d\n\x18\x45\x34\x31\x31\x32_RIGHT_BUMPER_STUCK\x10\x90 \x12\x1c\n\x17\x45\x34\x31\x33\x30_LASER_COVER_STUCK\x10\xa2 \x12 \n\x1b\x45\x35\x30\x31\x34_LOW_BATTERY_SHUT_DOWN\x10\x96\'\x12\'\n\"E5015_LOW_BATTERY_SCHEDULES_FAILED\x10\x97\'\x12\"\n\x1d\x45\x35\x31\x31\x30_WIFI_OR_BLUETOOTH_ERROR\x10\xf6\'\x12&\n!E5112_STATION_COMMUNICATION_ERROR\x10\xf8\'\x12 \n\x1b\x45\x36\x31\x31\x33_NO_DUST_BAG_INSTALLED\x10\xe1/\x12\x1f\n\x1a\x45\x36\x33\x31\x30_CUT_HAIR_INTERRUPTED\x10\xa6\x31\x12\x19\n\x14\x45\x36\x33\x31\x31_CUT_HAIR_STUCK\x10\xa7\x31\x12\x18\n\x13\x45\x37\x30\x30\x30_ROBOT_TRAPPED\x10\xd8\x36\x12\x1f\n\x1a\x45\x37\x30\x30\x31_ROBOT_PARTLY_SUSPEND\x10\xd9\x36\x12\x18\n\x13\x45\x37\x30\x30\x32_ROBOT_SUSPEND\x10\xda\x36\x12 \n\x1b\x45\x37\x30\x30\x33_ROBOT_STARTUP_SUSPEND\x10\xdb\x36\x12\x1d\n\x18\x45\x37\x30\x31\x30_ENTERED_NO_GO_ZONE\x10\xe2\x36\x12\x30\n+E7020_POSITIONING_FAILED_AND_START_CLEANING\x10\xec\x36\x12.\n)E7021_POSITIONING_FAILED_AND_HEADING_HOME\x10\xed\x36\x12\x18\n\x13\x45\x37\x30\x33\x31_RETURN_FAILED\x10\xf7\x36\x12\x35\n0E7032_FIND_STATION_FAILED_AND_RETURN_START_POINT\x10\xf8\x36\x12)\n$E7033_RETURN_STATION_FAILED_AND_STOP\x10\xf9\x36\x12+\n&E7034_FINE_START_POINT_FAILED_AND_STOP\x10\xfa\x36\x12\x1f\n\x1a\x45\x37\x30\x34\x30_LEAVE_STATION_FAILED\x10\x80\x37\x12)\n$E7050_INACCESSIBLE_AREAS_NOT_CLEANED\x10\x8a\x37\x12#\n\x1e\x45\x37\x30\x35\x31_IN_TASK_SCHEDULES_FAILED\x10\x8b\x37\x12\x1c\n\x17\x45\x37\x30\x35\x32_ROUTE_UNAVAILABLE\x10\x8c\x37*\xd5\x02\n\x0ePromptCodeList\x12\x0e\n\nP0000_NONE\x10\x00\x12 \n\x1cP0031_POSITIONING_SUCCESSFUL\x10\x1f\x12$\n P0040_TASK_FINISHED_HEADING_HOME\x10(\x12#\n\x1fP0076_NO_PERFORMANCE_AT_STATION\x10L\x12#\n\x1fP0078_LOW_BATTERY_NEED_CHARGING\x10N\x12\"\n\x1eP0079_LOW_BATTERY_HEADING_HOME\x10O\x12\x1c\n\x18P0085_SCHEDULED_CLEANING\x10U\x12 \n\x1cP0087_MAP_UPDATING_TRY_LATER\x10W\x12$\n\x1fP6301_LOW_BATTERY_CANT_CUT_HAIR\x10\x9d\x31\x12\x17\n\x12P6300_CUTTING_HAIR\x10\x9c\x31\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.cloud.error_code_list_t2265_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_ERRORCODELIST']._serialized_start=63
  _globals['_ERRORCODELIST']._serialized_end=1915
  _globals['_PROMPTCODELIST']._serialized_start=1918
  _globals['_PROMPTCODELIST']._serialized_end=2259
# @@protoc_insertion_point(module_scope)