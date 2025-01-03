"""Utility functions for Eufy Clean Vacuum."""
import base64
import logging
from typing import Any, Dict, List, Optional

from .proto.cloud import (
    work_status_pb2,
    clean_param_pb2,
    map_edit_pb2,
    map_manage_pb2,
    multi_maps_pb2,
    app_device_info_pb2,
)

_LOGGER = logging.getLogger(__name__)

async def decode_protobuf(proto_module: str, message_type: str, data: str) -> Optional[Dict[str, Any]]:
    """Decode protobuf data using generated classes."""
    try:
        # Map proto module names to their modules
        proto_modules = {
            'work_status': work_status_pb2,
            'clean_param': clean_param_pb2,
            'map_edit': map_edit_pb2,
            'map_manage': map_manage_pb2,
            'multi_maps': multi_maps_pb2,
            'app_device_info': app_device_info_pb2,
        }

        if proto_module not in proto_modules:
            _LOGGER.error("Proto module %s is not supported", proto_module)
            return None

        module = proto_modules[proto_module]

        # Get the message class
        message_class = getattr(module, message_type, None)
        if not message_class:
            _LOGGER.error("Message type %s not found in %s module", message_type, proto_module)
            return None

        # Decode base64 data
        binary_data = base64.b64decode(data)

        # Parse the message
        message = message_class()
        message.ParseFromString(binary_data)

        # Convert to dict
        return message_to_dict(message)
    except Exception as err:
        _LOGGER.error("Error decoding protobuf data: %s", err)
        return None

def message_to_dict(message: Any) -> Dict[str, Any]:
    """Convert protobuf message to dictionary."""
    result = {}
    for field in message.DESCRIPTOR.fields:
        if not message.HasField(field.name):
            continue

        value = getattr(message, field.name)
        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[field.name] = [message_to_dict(item) for item in value]
            else:
                result[field.name] = message_to_dict(value)
        elif field.type == field.TYPE_ENUM:
            # Get enum name for enum fields
            enum_type = field.enum_type
            result[field.name] = enum_type.values_by_number[value].name.lower()
        else:
            result[field.name] = value
    return result

async def get_multi_data(proto_module: str, message_type: str, data: str) -> List[Dict[str, Any]]:
    """Get multiple data fields from protobuf message."""
    decoded = await decode_protobuf(proto_module, message_type, data)
    if not decoded:
        return []

    result = []
    for key, value in decoded.items():
        if isinstance(value, dict):
            result.append({"key": key, "value": value})
        else:
            result.append({"key": key, "value": value})
    return result

async def decode_dps_protos(dps: Dict[str, Any]) -> Dict[str, Any]:
    """Decode protobuf messages in DPS values."""
    decoded = {}

    # Map of DPS keys to their proto modules and message types
    DPS_PROTO_MAP = {
        "153": ("clean_param", "CleanParam"),
        "154": ("clean_param", "CleanParamResponse"),
        "157": ("work_status", "WorkStatus"),
        "164": ("map_edit", "MapInfo"),
        "165": ("multi_maps", "RoomInfo"),
        "169": ("app_device_info", "DeviceInfo")
    }

    for dps_key, value in dps.items():
        if dps_key in DPS_PROTO_MAP and value:
            try:
                proto_module, message_type = DPS_PROTO_MAP[dps_key]
                decoded_value = await decode_protobuf(proto_module, message_type, value)
                if decoded_value:
                    decoded[dps_key] = decoded_value
            except Exception as e:
                _LOGGER.warning(f"Failed to decode DPS {dps_key}: {e}")
                decoded[dps_key] = value
        else:
            decoded[dps_key] = value

    return decoded
