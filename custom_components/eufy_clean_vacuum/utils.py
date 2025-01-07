"""Utility functions for the Eufy Clean Vacuum integration."""

import base64
import os
import logging
from typing import Any, Dict, Optional, Type, Union, List
from google.protobuf import message
from google.protobuf.message import Message
import importlib

_LOGGER = logging.getLogger(__name__)

# DPS to Proto mapping
DPS_PROTO_MAP = {
    "153": ("proto.cloud.clean_param", "CleanParam"),
    "154": ("proto.cloud.clean_param", "CleanParamResponse"),
    "157": ("proto.cloud.work_status", "WorkStatus"),
    "164": ("proto.cloud.map_edit", "MapInfo"),
    "165": ("proto.cloud.multi_maps", "RoomInfo"),
    "169": ("proto.cloud.app_device_info", "DeviceInfo"),
    "173": ("proto.cloud.clean_record", "CleanRecord"),
    "176": ("proto.cloud.clean_record_wrap", "CleanRecordWrap"),
    "177": ("proto.cloud.clean_statistics", "CleanStatistics"),
    "178": ("proto.cloud.clean_statistics", "CleanStatisticsResponse"),
    "179": ("proto.cloud.consumable", "ConsumableInfo"),
    "180": ("proto.cloud.scene", "SceneInfo")
}

# Map proto module names to their import paths
PROTO_MODULE_MAP = {
    'work_status': 'proto.cloud.work_status',
    'clean_param': 'proto.cloud.clean_param',
    'map_edit': 'proto.cloud.map_edit',
    'map_manage': 'proto.cloud.map_manage',
    'multi_maps': 'proto.cloud.multi_maps',
    'app_device_info': 'proto.cloud.app_device_info',
}

def get_proto_class(proto_path: str, message_type: str) -> Type[Message]:
    """Get the protobuf class for a given message type."""
    try:
        # Import the module
        module = importlib.import_module(proto_path)
        # Get the message class from the module
        message_class = getattr(module, message_type)
        return message_class
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load protobuf class: {e}")

async def decode_protobuf(proto_module: str, message_type: str, data: str) -> Optional[Dict[str, Any]]:
    """Decode protobuf data using generated classes."""
    try:
        if proto_module not in PROTO_MODULE_MAP:
            _LOGGER.error("Proto module %s is not supported", proto_module)
            return None

        module_path = PROTO_MODULE_MAP[proto_module]
        decoded = decode(module_path, message_type, data)
        return decoded
    except Exception as err:
        _LOGGER.error("Error decoding protobuf data: %s", err)
        return None

def decode(proto_path: str, message_type: str, base64_value: str) -> Dict[str, Any]:
    """Decode a base64 encoded protobuf message."""
    try:
        # Get the protobuf class
        proto_class = get_proto_class(proto_path, message_type)

        # Decode base64 to bytes
        buffer = base64.b64decode(base64_value)

        # Create a new message instance
        message = proto_class()

        # Parse the delimited message
        message.ParseFromString(buffer)

        # Convert to dictionary
        return message_to_dict(message)
    except Exception as e:
        _LOGGER.error(f"Failed to decode protobuf message: {e}")
        return None

def encode(proto_path: str, message_type: str, data: Dict[str, Any]) -> str:
    """Encode a dictionary to a base64 encoded protobuf message."""
    try:
        # Get the protobuf class
        proto_class = get_proto_class(proto_path, message_type)

        # Create a new message instance and populate it
        message = proto_class()
        dict_to_message(data, message)

        # Serialize the message
        buffer = message.SerializeToString()

        # Encode to base64
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        _LOGGER.error(f"Failed to encode protobuf message: {e}")
        return None

def message_to_dict(message: Message) -> Dict[str, Any]:
    """Convert a protobuf message to a dictionary."""
    result = {}
    for field in message.DESCRIPTOR.fields:
        value = getattr(message, field.name)
        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[field.name] = [message_to_dict(item) for item in value]
            else:
                result[field.name] = message_to_dict(value) if value.ByteSize() else None
        elif field.type == field.TYPE_ENUM:
            result[field.name] = field.enum_type.values_by_number[value].name
        elif field.label == field.LABEL_REPEATED:
            result[field.name] = list(value)
        else:
            result[field.name] = value
    return result

def dict_to_message(data: Dict[str, Any], message: Message) -> None:
    """Populate a protobuf message from a dictionary."""
    for field in message.DESCRIPTOR.fields:
        if field.name not in data:
            continue

        value = data[field.name]
        if value is None:
            continue

        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                for item in value:
                    sub_message = getattr(message, field.name).add()
                    dict_to_message(item, sub_message)
            else:
                dict_to_message(value, getattr(message, field.name))
        elif field.type == field.TYPE_ENUM:
            enum_value = field.enum_type.values_by_name[value].number
            setattr(message, field.name, enum_value)
        else:
            setattr(message, field.name, value)

def get_key_by_value(dictionary: Dict[Any, Any], value: Any) -> Optional[Any]:
    """Get a key in a dictionary by its value."""
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def decode_dps_protos(dps: Dict[str, Any]) -> Dict[str, Any]:
    """Decode protobuf messages in DPS values."""
    decoded = {}

    for dps_key, value in dps.items():
        if dps_key in DPS_PROTO_MAP and value and isinstance(value, str):
            try:
                proto_module, message_type = DPS_PROTO_MAP[dps_key]
                decoded_value = decode(proto_module, message_type, value)
                if decoded_value:
                    decoded[dps_key] = decoded_value
                else:
                    decoded[dps_key] = value
            except Exception as e:
                _LOGGER.warning(f"Failed to decode DPS {dps_key}: {e}")
                decoded[dps_key] = value
        else:
            decoded[dps_key] = value

    return decoded

def get_multi_data(proto_path: str, message_type: str, base64_value: str) -> List[Dict[str, Any]]:
    """Get multiple data fields from protobuf message."""
    decoded = decode(proto_path, message_type, base64_value)
    if not decoded:
        return []

    result = []
    for key, value in decoded.items():
        if isinstance(value, dict):
            result.append({"key": key, **value})
        else:
            result.append({"key": key, "value": value})
    return result
