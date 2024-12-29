from typing import Dict, Any
from .base import Base

class LocalConnect(Base):
    def __init__(self, config: Dict[str, Any]):
        """Initialize local connection controller.

        Note: This connection type is deprecated, use CloudConnect instead.

        Args:
            config: Configuration dictionary containing device settings
        """
        super().__init__(config)
        print("WARNING: LocalConnect is deprecated, use CloudConnect instead")

        self.device_id = config['device_id']
        self.device_model = config.get('device_model', '')
        self.config = config
        self.local_key = config.get('local_key', '')
        self.ip = config.get('ip', '')

    async def connect(self) -> None:
        """Establish local connection to the device."""
        print("WARNING: LocalConnect is deprecated, use CloudConnect instead")
        pass

    async def send_command(self, data: Dict[str, Any]) -> None:
        """Send command to the device locally.

        Args:
            data: Command data to send
        """
        print("WARNING: LocalConnect is deprecated, use CloudConnect instead")
        pass
