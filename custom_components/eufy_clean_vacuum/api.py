"""Eufy Clean API client."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, TypedDict, Optional, Union

from .login import EufyLogin

_LOGGER = logging.getLogger(__name__)

class EufyCloudDeviceProduct(TypedDict):
    """Type for Eufy cloud device product data."""
    id: str
    name: str
    product_code: str
    region: str
    default_name: str
    icon_url: str
    category: str
    appliance: str
    connect_type: int
    description: str
    wifi_ssid_prefix: str

class EufyCloudDeviceRawData(TypedDict):
    """Type for Eufy cloud device raw data."""
    id: str
    sn: str
    name: str
    alias_name: str
    product: EufyCloudDeviceProduct
    user_id: str
    home_id: str
    room_id: str
    connect_type: int
    online: bool

class EufyCloudDevice(TypedDict):
    """Type for mapped cloud device data."""
    device_sn: str
    deviceName: str
    deviceModel: str
    product_code: str
    online: bool
    dps: Dict[str, Any]
    mqtt: bool
    raw_data: EufyCloudDeviceRawData

class EufyMqttDevice(TypedDict):
    """Type for MQTT device data."""
    device_sn: str
    deviceModel: str
    deviceName: str
    dps: Dict[str, Any]
    mqtt: bool
    is_online: bool
    state: str
    battery_level: Optional[int]
    is_novel_api: bool
    product_code: str
    type: str

class EufyCleanApi:
    """Eufy Clean API client."""

    def __init__(self, username: str, password: str, locale: str = "en") -> None:
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.locale = locale
        openudid = str(uuid.uuid4())
        self.login = EufyLogin(username, password, openudid, locale)
        self.mqtt_credentials = None

    async def init(self) -> None:
        """Initialize the API connection."""
        try:
            await self.login.init()
            self.mqtt_credentials = self.login.mqtt_credentials
            _LOGGER.debug("Successfully initialized API connection")
        except Exception as err:
            _LOGGER.error("Failed to initialize API connection: %s", err)
            await self.close()
            raise

    async def get_cloud_devices(self) -> List[EufyCloudDevice]:
        """Get list of devices from cloud API."""
        try:
            _LOGGER.info("[CLOUD] Fetching devices")
            # Get devices from login class
            if not hasattr(self.login, 'cloud_devices'):
                _LOGGER.warning("[CLOUD] No cloud_devices attribute in login class")
                return []

            devices = self.login.cloud_devices
            _LOGGER.info("[CLOUD] Raw devices from login class: %s", devices)

            # Map devices to our format
            mapped_devices: List[EufyCloudDevice] = []
            for device in devices:
                try:
                    _LOGGER.debug("[CLOUD] Processing device: %s", device)

                    # First try to get device_sn from the top level
                    device_sn = device.get("device_sn")
                    _LOGGER.debug("[CLOUD] Top level device_sn: %s", device_sn)

                    raw_data = device.get("raw_data", {})
                    _LOGGER.debug("[CLOUD] Raw data layer 1: %s", raw_data)

                    # If we have nested raw_data, get the inner layer
                    inner_raw_data = raw_data.get("raw_data", {})
                    if inner_raw_data:
                        _LOGGER.info("[CLOUD] Found nested raw_data, using inner layer")
                        _LOGGER.debug("[CLOUD] Raw data layer 2: %s", inner_raw_data)

                        # If we didn't get device_sn from top level, try the inner raw_data
                        if not device_sn:
                            device_sn = inner_raw_data.get("id")
                            _LOGGER.debug("[CLOUD] Using device ID from inner layer: %s", device_sn)

                        product_data = inner_raw_data.get("product", {})
                        device_name = inner_raw_data.get("name", "")
                        connect_type = inner_raw_data.get("connect_type", 0)
                    else:
                        product_data = raw_data.get("product", {})
                        device_name = raw_data.get("name", "")
                        connect_type = raw_data.get("connect_type", 0)

                    _LOGGER.debug("[CLOUD] Product data: %s", product_data)

                    device_data: EufyCloudDevice = {
                        "device_sn": device_sn,
                        "deviceName": device_name,
                        "deviceModel": product_data.get("name", ""),
                        "product_code": product_data.get("product_code", ""),
                        "online": connect_type > 0,
                        "dps": device.get("dps", {}),
                        "mqtt": False,
                        "raw_data": inner_raw_data if inner_raw_data else raw_data
                    }
                    _LOGGER.info("[CLOUD] Mapped device data: %s", device_data)

                    if not device_sn:
                        _LOGGER.warning("[CLOUD] Device ID missing from mapped data: %s", device_data)
                        continue

                    mapped_devices.append(device_data)
                except Exception as err:
                    _LOGGER.error("[CLOUD] Error mapping device data: %s", err, exc_info=True)
                    continue

            _LOGGER.info("[CLOUD] Successfully mapped %d devices", len(mapped_devices))
            return mapped_devices

        except Exception as err:
            _LOGGER.error("[CLOUD] Error getting devices: %s", err, exc_info=True)
            return []

    async def get_mqtt_devices(self) -> List[EufyMqttDevice]:
        """Get MQTT devices."""
        try:
            _LOGGER.info("[MQTT] Getting devices")
            if not hasattr(self.login, 'mqtt_devices'):
                _LOGGER.warning("[MQTT] No mqtt_devices attribute in login class")
                return []

            devices = self.login.mqtt_devices
            _LOGGER.info("[MQTT] Raw devices from login class: %s", devices)

            # Map devices to our format
            mapped_devices: List[EufyMqttDevice] = []
            for device in devices:
                try:
                    _LOGGER.debug("[MQTT] Processing device: %s", device)
                    device_sn = device.get("device_sn")
                    _LOGGER.info("[MQTT] Extracted device_sn: %s", device_sn)

                    mqtt_device: EufyMqttDevice = {
                        "device_sn": device_sn,
                        "deviceModel": device.get("deviceModel", ""),
                        "deviceName": device.get("deviceName", ""),
                        "dps": device.get("dps", {}),
                        "mqtt": True,
                        "is_online": device.get("online", True),
                        "state": device.get("state", "unknown"),
                        "battery_level": device.get("battery_level"),
                        "is_novel_api": device.get("apiType") == "novel",
                        "product_code": device.get("deviceModel", ""),
                        "type": "mqtt"
                    }
                    _LOGGER.info("[MQTT] Mapped device data: %s", mqtt_device)

                    if not device_sn:
                        _LOGGER.warning("[MQTT] Device ID missing from mapped data: %s", mqtt_device)
                        continue

                    mapped_devices.append(mqtt_device)
                except Exception as err:
                    _LOGGER.error("[MQTT] Error mapping device data: %s", err, exc_info=True)
                    continue

            _LOGGER.info("[MQTT] Successfully mapped %d devices", len(mapped_devices))
            return mapped_devices

        except Exception as err:
            _LOGGER.error("[MQTT] Error getting devices: %s", err, exc_info=True)
            return []

    async def get_all_devices(self) -> List[Union[EufyCloudDevice, EufyMqttDevice]]:
        """Get all devices."""
        cloud_devices = await self.get_cloud_devices()
        mqtt_devices = await self.get_mqtt_devices()
        return [*cloud_devices, *mqtt_devices]

    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status."""
        try:
            # Try MQTT first
            mqtt_device = await self.login.get_mqtt_device(device_id)
            if mqtt_device:
                _LOGGER.info("[MQTT] Got device status for %s: %s", device_id, mqtt_device)
                return {
                    "dps": mqtt_device.get("dps", {}),
                    "status": mqtt_device.get("device_status"),
                    "battery_level": mqtt_device.get("rate", 100),
                }

            # Fall back to cloud
            cloud_device = next(
                (d for d in self.login.cloud_devices if d.get("device_sn") == device_id), None
            )
            if cloud_device:
                _LOGGER.info("[CLOUD] Got device status for %s: %s", device_id, cloud_device)
                return {
                    "dps": cloud_device.get("dps", {}),
                    "status": cloud_device.get("status"),
                    "battery_level": cloud_device.get("battery", 100),
                }

            return {}
        except Exception as err:
            _LOGGER.error("Error getting device status: %s", err)
            return {}

    async def send_command(self, device_id: str, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        try:
            _LOGGER.info("Sending command to device %s: %s", device_id, dps)
            await self.login.send_command(device_id, dps)
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            raise

    async def close(self) -> None:
        """Close the API connection."""
        await self.login.close()

__all__ = ["EufyCleanApi", "EufyCloudDevice", "EufyMqttDevice"]
