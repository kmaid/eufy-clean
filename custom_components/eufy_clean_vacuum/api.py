"""Eufy Clean API client."""
import logging
import uuid
from typing import Any, Dict, List, Optional

from .login import EufyLogin

_LOGGER = logging.getLogger(__name__)

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

    async def get_cloud_devices(self) -> List[Dict[str, Any]]:
        """Get cloud devices."""
        devices = []
        for device in self.login.cloud_devices:
            device_id = device.get("devId")
            if device_id:
                devices.append({
                    "device_sn": device_id,  # Use device_sn consistently
                    "deviceModel": device.get("deviceModel", ""),
                    "deviceName": device.get("alias_name") or device.get("device_name") or device.get("name", ""),
                    "dps": device.get("dps", {}),
                    "mqtt": False
                })
        return devices

    async def get_mqtt_devices(self) -> List[Dict[str, Any]]:
        """Get list of MQTT devices."""
        if not self.login.mqtt_connect:
            _LOGGER.warning("No MQTT connection available")
            return []

        # Get cloud devices first to get device model
        cloud_devices = await self.get_cloud_devices()
        if cloud_devices:
            device = cloud_devices[0]  # Use first device for now
            device_id = device.get("device_sn")
            device_model = device.get("deviceModel")
            if device_id and device_model:
                _LOGGER.info("Setting up MQTT with device info - ID: %s, Model: %s", device_id, device_model)
                # First set device info
                await self.login.mqtt_connect.set_device_info(device_id, device_model)
                # Then connect
                await self.login.mqtt_connect.connect()
            else:
                _LOGGER.warning("Could not get device info from cloud device: %s", device)
                await self.login.mqtt_connect.connect()
        else:
            _LOGGER.warning("No cloud devices found for MQTT connection")
            await self.login.mqtt_connect.connect()

        return await self.login.mqtt_connect.get_device_list()

    async def get_all_devices(self) -> List[Dict[str, Any]]:
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
                return {
                    "dps": mqtt_device.get("dps", {}),
                    "status": mqtt_device.get("device_status"),
                    "battery_level": mqtt_device.get("rate", 100),
                }

            # Fall back to cloud
            cloud_device = next(
                (d for d in self.login.cloud_devices if d.get("devId") == device_id), None
            )
            if cloud_device:
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
            await self.login.send_command(device_id, dps)
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            raise

    async def close(self) -> None:
        """Close the API connection."""
        await self.login.close()

__all__ = ["EufyCleanApi"]
