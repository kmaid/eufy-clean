from typing import Dict, Any, Optional
from .base import Base
from .login import EufyLogin

class CloudConnect(Base):
    def __init__(self, config: Dict[str, Any], eufy_clean_api: EufyLogin):
        """Initialize cloud connection controller.

        Args:
            config: Configuration dictionary containing device settings
            eufy_clean_api: Instance of EufyLogin for API access
        """
        super().__init__(config)

        self.device_id = config['device_id']
        self.device_model = config.get('device_model', '')
        self.config = config

        self.auto_update = config.get('auto_update', 0)
        self.debug_log = config.get('debug', False)
        self.eufy_clean_api = eufy_clean_api

    async def connect(self) -> None:
        """Establish connection to the device."""
        await self.update_device(True)

    async def update_device(self, check_api_type: bool = False) -> None:
        """Update device information.

        Args:
            check_api_type: Whether to check the API type
        """
        try:
            device = await self.eufy_clean_api.get_cloud_device(self.device_id)

            if check_api_type:
                await self.check_api_type(device.get('dps', {}))

            await self.map_data(device.get('dps', {}))
        except Exception as error:
            print(error)

    async def send_command(self, data: Dict[str, Any]) -> None:
        """Send command to the device.

        Args:
            data: Command data to send
        """
        try:
            await self.eufy_clean_api.send_cloud_command(self.device_id, data)
        except Exception as error:
            print(error)
