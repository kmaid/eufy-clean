"""Eufy Clean API client."""
import logging
from typing import Dict, List, Optional
import uuid

from .controllers.login import EufyLogin
from .controllers.mqtt_connect import MqttConnect
from .controllers.local_connect import LocalConnect
from .controllers.cloud_connect import CloudConnect

_LOGGER = logging.getLogger(__name__)


class EufyClean:
    """Eufy Clean API client."""

    def __init__(self, username: str, password: str, openudid: Optional[str] = None):
        """Initialize Eufy Clean API client.

        Args:
            username: Eufy account email
            password: Eufy account password
            openudid: Optional unique device identifier
        """
        if not openudid:
            openudid = str(uuid.uuid4())

        self.eufy_login = EufyLogin(username, password, openudid)
        self.mqtt_connect: Optional[MqttConnect] = None

    async def init(self) -> None:
        """Initialize connection and fetch device lists."""
        await self.eufy_login.init()

    async def get_mqtt_devices(self) -> List[Dict]:
        """Get list of MQTT-connected devices."""
        return await self.eufy_login.get_device_list()

    async def get_cloud_devices(self) -> List[Dict]:
        """Get list of cloud-connected devices."""
        return await self.eufy_login.get_cloud_device_list()

    async def get_device_properties(self, device_model: str) -> None:
        """Get device properties."""
        return await self.eufy_login.get_device_properties(device_model)

    async def get_mqtt_credentials(self) -> Dict:
        """Get MQTT credentials."""
        return await self.eufy_login.get_mqtt_credentials()

    async def get_user_info(self) -> Dict:
        """Get user information."""
        return await self.eufy_login.get_user_info()

    async def get_cloud_device(self, device_id: str) -> Optional[Dict]:
        """Get cloud device by ID."""
        return await self.eufy_login.get_cloud_device(device_id)

    async def send_cloud_command(self, device_id: str, command: Dict) -> None:
        """Send command to cloud device."""
        await self.eufy_login.send_cloud_command(device_id, command)
