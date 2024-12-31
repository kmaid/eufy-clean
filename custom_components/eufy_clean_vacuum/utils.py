"""Utility functions for Eufy Clean Vacuum."""
import base64
import logging
import os
import shutil
import asyncio
from typing import Any, Dict, List, Optional

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory, text_format

_LOGGER = logging.getLogger(__name__)

async def get_proto_path(proto_file: str) -> str:
    """Get the absolute path to a proto file."""
    # Get the path to the custom component directory
    component_dir = os.path.dirname(__file__)
    proto_dir = os.path.join(component_dir, "proto", "cloud")

    # Create proto directory if it doesn't exist
    await asyncio.get_event_loop().run_in_executor(None, lambda: os.makedirs(proto_dir, exist_ok=True))

    proto_path = os.path.join(proto_dir, proto_file)

    # If the proto file doesn't exist, copy it from the original source
    if not os.path.exists(proto_path):
        _LOGGER.error("Proto file not found: %s", proto_path)
        return proto_path

    return proto_path

async def decode_protobuf(proto_file: str, message_type: str, data: str) -> Optional[Dict[str, Any]]:
    """Decode protobuf data."""
    try:
        # Load the proto file
        proto_path = await get_proto_path(proto_file)
        proto_content = await asyncio.get_event_loop().run_in_executor(None, lambda: open(proto_path, "r").read())

        # Create a FileDescriptorSet
        file_set = descriptor_pb2.FileDescriptorSet()
        text_format.Parse(proto_content, file_set)

        # Create a descriptor pool
        pool = descriptor_pool.DescriptorPool()
        for file_desc in file_set.file:
            pool.Add(file_desc)

        # Get the message descriptor
        desc = pool.FindMessageTypeByName(message_type)
        if not desc:
            _LOGGER.error("Message type %s not found in proto file", message_type)
            return None

        # Create a message factory
        factory = message_factory.MessageFactory(pool)
        message_class = factory.GetPrototype(desc)

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
        value = getattr(message, field.name)
        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[field.name] = [message_to_dict(item) for item in value]
            else:
                result[field.name] = message_to_dict(value)
        else:
            result[field.name] = value
    return result

async def get_multi_data(proto_file: str, message_type: str, data: str) -> List[Dict[str, Any]]:
    """Get multiple data fields from protobuf message."""
    decoded = await decode_protobuf(proto_file, message_type, data)
    if not decoded:
        return []

    result = []
    for key, value in decoded.items():
        if isinstance(value, dict):
            result.append({"key": key, "value": value})
        else:
            result.append({"key": key, "value": value})
    return result
