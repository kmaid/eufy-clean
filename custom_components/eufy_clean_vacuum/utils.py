"""Utility functions for the Eufy Clean Vacuum integration."""

import base64
import os
import logging
import sys
from typing import Any, Dict, Optional, Type, Union, List
from google.protobuf import message
from google.protobuf.message import Message
import importlib
from pathlib import Path
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.message_factory import GetMessageClass

_LOGGER = logging.getLogger(__name__)

# Map proto module names to their import paths
PROTO_MODULE_MAP = {
    'work_status': 'custom_components.eufy_clean_vacuum.proto.cloud.work_status_pb2',
    'clean_param': 'custom_components.eufy_clean_vacuum.proto.cloud.clean_param_pb2',
    'map_edit': 'custom_components.eufy_clean_vacuum.proto.cloud.map_edit_pb2',
    'map_manage': 'custom_components.eufy_clean_vacuum.proto.cloud.map_manage_pb2',
    'multi_maps': 'custom_components.eufy_clean_vacuum.proto.cloud.multi_maps_pb2',
    'app_device_info': 'custom_components.eufy_clean_vacuum.proto.cloud.app_device_info_pb2',
    'clean_record': 'custom_components.eufy_clean_vacuum.proto.cloud.clean_record_pb2',
    'clean_record_wrap': 'custom_components.eufy_clean_vacuum.proto.cloud.clean_record_wrap_pb2',
    'clean_statistics': 'custom_components.eufy_clean_vacuum.proto.cloud.clean_statistics_pb2',
    'consumable': 'custom_components.eufy_clean_vacuum.proto.cloud.consumable_pb2',
    'scene': 'custom_components.eufy_clean_vacuum.proto.cloud.scene_pb2'
}

# DPS to Proto mapping
DPS_PROTO_MAP = {
    "153": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_param_pb2", "CleanParam"),
    "154": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_param_pb2", "CleanParam"),
    "157": ("custom_components.eufy_clean_vacuum.proto.cloud.work_status_pb2", "WorkStatus"),
    "164": ("custom_components.eufy_clean_vacuum.proto.cloud.map_edit_pb2", "MapEditRequest"),
    "165": ("custom_components.eufy_clean_vacuum.proto.cloud.multi_maps_pb2", "MultiMapsManageRequest"),
    "169": ("custom_components.eufy_clean_vacuum.proto.cloud.app_device_info_pb2", "DeviceInfo"),
    "173": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_record_pb2", "CleanRecordData"),
    "176": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_record_wrap_pb2", "CleanRecordWrap"),
    "177": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_statistics_pb2", "CleanStatistics"),
    "178": ("custom_components.eufy_clean_vacuum.proto.cloud.clean_statistics_pb2", "CleanStatistics"),
    "179": ("custom_components.eufy_clean_vacuum.proto.cloud.consumable_pb2", "ConsumableRequest"),
    "180": ("custom_components.eufy_clean_vacuum.proto.cloud.scene_pb2", "SceneRequest")
}

# Pre-load all protobuf modules
_PROTO_MODULES = {}
_DESCRIPTOR_POOL = _descriptor_pool.Default()

def load_proto_descriptors():
    """Load proto descriptors."""
    proto_dir = Path(__file__).parent / "proto"
    for file in proto_dir.glob("**/*.desc"):
        with open(file, "rb") as f:
            _DESCRIPTOR_POOL.Add(f.read())

def _load_proto_modules():
    """Pre-load all protobuf modules and register their descriptors with the global descriptor pool."""
    try:
        pool = _descriptor_pool.Default()
        for module_path in PROTO_MODULE_MAP.values():
            try:
                module = importlib.import_module(module_path)
                _PROTO_MODULES[module_path] = module
                _LOGGER.debug("Successfully loaded protobuf module: %s", module_path)
            except Exception as e:
                _LOGGER.error("Failed to load protobuf module %s: %s", module_path, e)
    except Exception as e:
        _LOGGER.error("Failed to initialize protobuf modules: %s", e)

# Load modules at initialization time
_load_proto_modules()

def get_proto_class(proto_path: str, message_type: str) -> Type[Message]:
    """Get the protobuf class for a given message type."""
    try:
        # Get the pre-loaded module
        if proto_path not in _PROTO_MODULES:
            _LOGGER.error("Protobuf module %s not pre-loaded", proto_path)
            _LOGGER.debug("Available modules: %s", list(_PROTO_MODULES.keys()))
            raise ValueError(f"Protobuf module {proto_path} not pre-loaded")

        module = _PROTO_MODULES[proto_path]

        # Get the message descriptor from the module
        if not hasattr(module, message_type):
            _LOGGER.error("Module %s does not have message type %s", proto_path, message_type)
            _LOGGER.debug("Available message types: %s", dir(module))
            raise ValueError(f"Message type {message_type} not found in module {proto_path}")

        # Get the descriptor from the module
        descriptor = getattr(module, message_type)

        # Create the message class from the descriptor
        message_class = GetMessageClass(descriptor.DESCRIPTOR)
        if not message_class:
            raise ValueError(f"Failed to create message class for {message_type}")

        _LOGGER.debug("Found message class %s in module %s", message_type, proto_path)
        return message_class
    except Exception as e:
        _LOGGER.error("Failed to load protobuf class: %s", e)
        _LOGGER.debug("Proto path: %s, Message type: %s", proto_path, message_type)
        raise ValueError(f"Failed to load protobuf class: {e}")

def decode(proto_path: str, message_type: str, base64_value: str) -> Dict[str, Any]:
    """Decode a base64 encoded length-delimited protobuf message."""
    try:
        # Decode base64 to bytes
        try:
            buffer = base64.b64decode(base64_value)
            _LOGGER.debug("Decoded base64 data for %s.%s: %s", proto_path, message_type, buffer.hex())
        except Exception as e:
            _LOGGER.error("Failed to decode base64 data: %s", e)
            return None

        # Get the message class directly from the module
        message_class = get_proto_class(proto_path, message_type)
        if not message_class:
            return None

        # Create and parse the message using ParseDelimitedFrom
        message_obj = message_class()
        try:
            from google.protobuf.internal.decoder import _DecodeVarint32
            from io import BytesIO

            stream = BytesIO(buffer)
            length, new_pos = _DecodeVarint32(buffer, 0)
            stream.seek(new_pos)
            message_obj.ParseFromString(stream.read(length))
            return message_to_dict(message_obj)
        except Exception as e:
            _LOGGER.error("Failed to parse message: %s", e)
            _LOGGER.debug("Message class: %s", message_class)
            _LOGGER.debug("Buffer hex: %s", buffer.hex())
            return None

    except Exception as e:
        _LOGGER.error("Failed to decode protobuf message: %s", e)
        return None

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

def encode(proto_path: str, message_type: str, data: Dict[str, Any]) -> str:
    """Encode a dictionary to a base64 encoded length-delimited protobuf message."""
    try:
        # Get the protobuf class
        proto_class = get_proto_class(proto_path, message_type)

        # Create a new message instance and populate it
        message = proto_class()
        dict_to_message(data, message)

        # Get the size of the message
        size = message.ByteSize()
        _LOGGER.debug("Message size: %d bytes", size)

        # Create a buffer to hold the length-delimited message
        from google.protobuf.internal.encoder import _VarintBytes
        from io import BytesIO

        # Create a buffer with the length prefix
        buffer = BytesIO()
        buffer.write(_VarintBytes(size))
        buffer.write(message.SerializeToString())

        # Get the complete buffer
        result = buffer.getvalue()
        _LOGGER.debug("Encoded message (hex): %s", result.hex())

        # Encode to base64
        encoded = base64.b64encode(result).decode('utf-8')
        _LOGGER.debug("Base64 encoded result: %s", encoded)
        return encoded
    except Exception as e:
        _LOGGER.error("Failed to encode protobuf message: %s", e, exc_info=True)
        return None

def message_to_dict(message: Message) -> Dict[str, Any]:
    """Convert a protobuf message to a dictionary."""
    result = {}
    for field in message.DESCRIPTOR.fields:
        try:
            value = getattr(message, field.name)
            if field.type == field.TYPE_MESSAGE:
                if field.label == field.LABEL_REPEATED:
                    # Handle repeated message fields
                    result[field.name] = [message_to_dict(item) if hasattr(item, 'DESCRIPTOR') else item for item in value]
                else:
                    # Handle single message fields
                    result[field.name] = message_to_dict(value) if value.ByteSize() else None
            elif field.type == field.TYPE_ENUM:
                if field.label == field.LABEL_REPEATED:
                    # Handle repeated enum fields
                    result[field.name] = [field.enum_type.values_by_number[item].name if isinstance(item, int) else item for item in value]
                else:
                    # Handle single enum fields
                    result[field.name] = field.enum_type.values_by_number[value].name if isinstance(value, int) else value
            elif field.label == field.LABEL_REPEATED:
                # Handle other repeated fields (convert to list)
                result[field.name] = list(value)
            else:
                # Handle all other fields
                result[field.name] = value
        except Exception as e:
            _LOGGER.debug(f"Error converting field {field.name}: {e}")
            result[field.name] = None
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

def decode_proto_message(descriptor, data):
    """Decode a proto message."""
    try:
        message_class = GetMessageClass(descriptor.DESCRIPTOR)
        message = message_class()
        message.ParseFromString(data)
        return message
    except Exception as ex:  # pylint: disable=broad-except
        _LOGGER.error("Failed to decode proto message: %s", ex)
        return None
