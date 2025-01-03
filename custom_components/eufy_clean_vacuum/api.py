"""API for Eufy Clean Vacuum."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from .login import EufyCleanLogin

_LOGGER = logging.getLogger(__name__)

class EufyCleanApi:
    """API for Eufy Clean Vacuum."""

    def __init__(self, username: str, password: str, locale: str = "en") -> None:
        """Initialize the API."""
        self.username = username
        self.password = password
        self.locale = locale
        openudid = str(uuid.uuid4())
        self.login = EufyCleanLogin(username, password, openudid, locale)
        self._devices: List[Dict[str, Any]] = []

    async def init(self) -> None:
        """Initialize the API connection."""
        await self.async_setup()

    async def async_setup(self) -> None:
        """Set up the API connection."""
        try:
            _LOGGER.debug("Initializing API connection")
            await self.login.init()
            _LOGGER.debug("API initialization successful")
        except Exception as err:
            _LOGGER.error("Failed to initialize API: %s", err)
            raise

    async def close(self) -> None:
        """Close the API connection."""
        if hasattr(self.login, 'close'):
            await self.login.close()

    async def async_get_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices."""
        try:
            # Get devices from login class
            mqtt_devices = self.login.mqtt_devices
            _LOGGER.debug("Got %d MQTT devices", len(mqtt_devices))

            # Update our stored device list
            self._devices = mqtt_devices
            return self._devices

        except Exception as err:
            _LOGGER.error("Error getting devices: %s", err)
            raise

    async def send_command(self, device_id: str, command: Dict[str, Any]) -> None:
        """Send command to device."""
        try:
            _LOGGER.debug("Sending command to device %s: %s", device_id, command)
            if self.login.mqtt_connect:
                await self.login.mqtt_connect.send_command(device_id, command)
            else:
                _LOGGER.error("No MQTT connection available")
                raise Exception("No MQTT connection available")
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            raise
