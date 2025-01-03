"""Utility functions for Eufy Clean Vacuum."""
import base64
import logging
from typing import Any, Dict, List, Optional

# Import only work_status_pb2 for now as it's the main one we need
# We'll add others as needed to avoid import cycles
from .proto.cloud import work_status_pb2

_LOGGER = logging.getLogger(__name__)

async def decode_protobuf(proto_module: str, message_type: str, data: str) -> Optional[Dict[str, Any]]:
    """Decode protobuf data using generated classes."""
    try:
        # For now, we only support work_status since that's what we mainly use
        if proto_module != 'work_status':
            _LOGGER.error("Only work_status proto module is currently supported")
            return None

        # Get the message class
        message_class = getattr(work_status_pb2, message_type, None)
        if not message_class:
            _LOGGER.error("Message type %s not found in work_status module", message_type)
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
