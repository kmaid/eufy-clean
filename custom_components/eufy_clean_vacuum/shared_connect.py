"""Shared connection handler."""
import logging
from typing import Any, Dict, Optional
import time

from .base import Base

_LOGGER = logging.getLogger(__name__)

class SharedConnect(Base):
    """Shared connection handler."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the shared connection."""
        super().__init__()
        self.device_id = config.get("device_id")
        self.device_model = config.get("device_model", "")
        self.debug = config.get("debug", False)
        self.novel_api = False
        self.robovac_data = {}
        self.mqtt_connect = None

    async def set_mqtt_connect(self, mqtt_connect) -> None:
        """Set MQTT connection."""
        self.mqtt_connect = mqtt_connect

    async def check_api_type(self, dps: Dict[str, Any]) -> None:
        """Check API type."""
        try:
            if not self.novel_api and any(k in dps for k in self.novel_dps_map.values()):
                _LOGGER.info("Novel API detected")
                await self.set_api_types(True)
            else:
                _LOGGER.info("Legacy API detected")
                await self.set_api_types(False)
        except Exception as err:
            _LOGGER.error("Error checking API type: %s", err)

    async def set_api_types(self, novel_api: bool) -> None:
        """Set API types."""
        self.novel_api = novel_api
        self.dps_map = self.novel_dps_map if novel_api else self.legacy_dps_map
        self.robovac_data = self.dps_map.copy()

    def map_data(self, dps: Dict[str, Any]) -> None:
        """Map DPS data."""
        if not dps:
            return

        for key, value in dps.items():
            mapped_keys = [k for k, v in self.dps_map.items() if v == key]
            for mapped_key in mapped_keys:
                self.robovac_data[mapped_key] = value

        if self.debug:
            _LOGGER.debug("Mapped data: %s", self.robovac_data)

    async def get_robovac_data(self) -> Dict[str, Any]:
        """Get robovac data."""
        return self.robovac_data

    async def get_battery_level(self) -> Optional[int]:
        """Get battery level."""
        return self.robovac_data.get("BATTERY_LEVEL")

    async def get_work_status(self) -> str:
        """Get work status."""
        return str(self.robovac_data.get("WORK_STATUS", "CHARGING")).lower()

    async def get_error_code(self) -> Optional[int]:
        """Get error code."""
        return self.robovac_data.get("ERROR_CODE", 0)

    async def play(self) -> None:
        """Start or resume cleaning."""
        value = True
        if self.novel_api:
            value = {
                "method": "RESUME_TASK"
            }
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def pause(self) -> None:
        """Pause cleaning."""
        value = False
        if self.novel_api:
            value = {
                "method": "PAUSE_TASK"
            }
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def stop(self) -> None:
        """Stop cleaning."""
        value = False
        if self.novel_api:
            value = {
                "method": "STOP_TASK"
            }
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def go_home(self) -> None:
        """Return to dock."""
        await self.send_command({self.dps_map["GO_HOME"]: True})

    async def send_command(self, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        if not self.mqtt_connect:
            _LOGGER.error("No MQTT connection available")
            return

        try:
            _LOGGER.debug("Sending command to device %s: %s", self.device_id, dps)
            await self.mqtt_connect.send_command(self.device_id, dps)
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
