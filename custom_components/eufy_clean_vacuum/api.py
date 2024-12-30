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
        return self.login.cloud_devices

    async def get_mqtt_devices(self) -> List[Dict[str, Any]]:
        """Get MQTT devices."""
        return self.login.mqtt_devices

    async def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all devices."""
        return [*self.login.cloud_devices, *self.login.mqtt_devices]

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
                (d for d in self.login.cloud_devices if d.get("id") == device_id), None
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
