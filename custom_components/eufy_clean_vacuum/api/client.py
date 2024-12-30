"""Eufy Clean API client."""
import logging
from typing import Dict, List, Optional
import uuid

from eufy_clean.controllers.login import EufyLogin
from eufy_clean.controllers.mqtt_connect import MqttConnect

_LOGGER = logging.getLogger(__name__)


class EufyClean:
    """Eufy Clean API client."""

    def __init__(self, username: str, password: str):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.openudid = str(uuid.uuid4())
        self.eufy_login = EufyLogin(username, password, self.openudid)
        self.mqtt_connect = None
        self.cloud_devices = []
        self.mqtt_devices = []

    async def init(self) -> None:
        """Initialize the connection."""
        await self.eufy_login.init()
        self.cloud_devices = self.eufy_login.cloud_devices
        self.mqtt_devices = self.eufy_login.mqtt_devices

        # Initialize MQTT connection if we have devices
        if self.mqtt_devices:
            mqtt_creds = await self.eufy_login.get_mqtt_credentials()
            if mqtt_creds:
                self.mqtt_connect = MqttConnect(mqtt_creds)
                await self.mqtt_connect.connect()

    async def get_mqtt_devices(self) -> List:
        """Get list of MQTT devices."""
        return self.mqtt_devices

    async def get_cloud_devices(self) -> List:
        """Get list of cloud devices."""
        return self.cloud_devices

    async def send_command(self, device_sn: str, command: Dict) -> None:
        """Send command to device.

        Args:
            device_sn: Device serial number
            command: Command data to send
        """
        if self.mqtt_connect:
            await self.mqtt_connect.send_command(device_sn, command)
        else:
            _LOGGER.error("MQTT connection not initialized")

    async def get_device_status(self, device_sn: str) -> Optional[Dict]:
        """Get device status.

        Args:
            device_sn: Device serial number

        Returns:
            Device status data or None if not found
        """
        if not self.mqtt_connect:
            return None

        try:
            status = await self.mqtt_connect.get_device_status(device_sn)
            if status:
                return {
                    "state": status.get("state", "STANDBY"),
                    "battery_level": status.get("battery", 0),
                    "status_message": status.get("status_message", ""),
                    "error_code": status.get("error_code"),
                }
        except Exception as err:
            _LOGGER.error("Failed to get device status: %s", err)

        return None
