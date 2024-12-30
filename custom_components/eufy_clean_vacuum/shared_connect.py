"""Shared connection class for Eufy Clean."""
import logging
from typing import Any, Dict, Optional

from .base import Base
from .constants import (
    EUFY_CLEAN_WORK_MODE,
    EUFY_CLEAN_NOVEL_CLEAN_SPEED,
    EUFY_CLEAN_CONTROL,
    EUFY_CLEAN_X_SERIES,
)

_LOGGER = logging.getLogger(__name__)

class SharedConnect(Base):
    """Shared connection class for Eufy Clean."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the shared connection."""
        super().__init__()
        self.novel_api = False
        self.robovac_data: Dict[str, Any] = {}
        self.debug_log = config.get("debug", False)
        self.device_id = config["device_id"]
        self.device_model = config.get("device_model", "")
        self.config = config

    async def check_api_type(self, dps: Dict[str, Any]) -> None:
        """Check which API type to use."""
        try:
            if not self.novel_api and any(k in dps for k in self.novel_dps_map.values()):
                _LOGGER.debug("Novel API detected")
                await self.set_api_types(True)
            else:
                _LOGGER.debug("Legacy API detected")
                await self.set_api_types(False)
        except Exception as err:
            _LOGGER.error("Error checking API type: %s", err)

    async def set_api_types(self, novel_api: bool) -> None:
        """Set API types."""
        self.novel_api = novel_api
        self.dps_map = self.novel_dps_map if novel_api else self.legacy_dps_map
        self.robovac_data = self.dps_map.copy()

    def map_data(self, dps: Dict[str, Any]) -> None:
        """Map DPS data to robovac data."""
        for key, value in dps.items():
            mapped_keys = [k for k, v in self.dps_map.items() if v == key]
            for mapped_key in mapped_keys:
                self.robovac_data[mapped_key] = value

        if self.debug_log:
            _LOGGER.debug("Mapped data: %s", self.robovac_data)

    async def get_robovac_data(self) -> Dict[str, Any]:
        """Get robovac data."""
        return self.robovac_data

    async def get_clean_speed(self) -> str:
        """Get clean speed."""
        if isinstance(self.robovac_data.get("CLEAN_SPEED"), (int, str)) and len(str(self.robovac_data.get("CLEAN_SPEED", ""))) == 1:
            clean_speeds = list(EUFY_CLEAN_NOVEL_CLEAN_SPEED.values())
            return clean_speeds[int(self.robovac_data["CLEAN_SPEED"])].lower()
        return (self.robovac_data.get("CLEAN_SPEED", "standard") or "standard").lower()

    async def get_play_pause(self) -> bool:
        """Get play/pause status."""
        return bool(self.robovac_data.get("PLAY_PAUSE", False))

    async def get_work_mode(self) -> str:
        """Get work mode."""
        try:
            if self.novel_api:
                # TODO: Implement proto decoding
                return "auto"
            return (self.robovac_data.get("WORK_MODE", "AUTO") or "AUTO").lower()
        except Exception:
            return "auto"

    async def get_work_status(self) -> str:
        """Get work status."""
        try:
            if self.novel_api:
                # TODO: Implement proto decoding
                return "charging"
            return (self.robovac_data.get("WORK_STATUS", "CHARGING") or "CHARGING").lower()
        except Exception:
            return "charging"

    async def get_battery_level(self) -> int:
        """Get battery level."""
        return int(self.robovac_data.get("BATTERY_LEVEL", 100))

    async def get_error_code(self) -> int:
        """Get error code."""
        try:
            if self.novel_api:
                # TODO: Implement proto decoding
                return 0
            return int(self.robovac_data.get("ERROR_CODE", 0))
        except Exception:
            return 0

    async def set_clean_speed(self, clean_speed: str) -> None:
        """Set clean speed."""
        try:
            if self.novel_api:
                clean_speeds = list(EUFY_CLEAN_NOVEL_CLEAN_SPEED.values())
                speed_index = clean_speeds.index(clean_speed.upper())
                await self.send_command({self.dps_map["CLEAN_SPEED"]: speed_index})
            else:
                await self.send_command({self.dps_map["CLEAN_SPEED"]: clean_speed})
        except Exception as err:
            _LOGGER.error("Error setting clean speed: %s", err)

    async def auto_clean(self) -> None:
        """Start auto clean."""
        if self.novel_api:
            # TODO: Implement proto encoding
            await self.send_command({self.dps_map["PLAY_PAUSE"]: True})
        else:
            await self.send_command({self.dps_map["WORK_MODE"]: EUFY_CLEAN_WORK_MODE["AUTO"]})
            await self.play()

    async def play(self) -> None:
        """Start cleaning."""
        value = True
        if self.novel_api:
            # TODO: Implement proto encoding for RESUME_TASK
            pass
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def pause(self) -> None:
        """Pause cleaning."""
        value = False
        if self.novel_api:
            # TODO: Implement proto encoding for PAUSE_TASK
            pass
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def stop(self) -> None:
        """Stop cleaning."""
        value = False
        if self.novel_api:
            # TODO: Implement proto encoding for STOP_TASK
            pass
        await self.send_command({self.dps_map["PLAY_PAUSE"]: value})

    async def go_home(self) -> None:
        """Send vacuum home."""
        if self.novel_api:
            # TODO: Implement proto encoding for START_GOHOME
            await self.send_command({self.dps_map["PLAY_PAUSE"]: True})
        else:
            await self.send_command({self.dps_map["GO_HOME"]: True})

    async def spot_clean(self) -> None:
        """Start spot cleaning."""
        if self.novel_api:
            # TODO: Implement proto encoding for START_SPOT_CLEAN
            await self.send_command({self.dps_map["PLAY_PAUSE"]: True})

    async def room_clean(self) -> None:
        """Start room cleaning."""
        if self.novel_api:
            # TODO: Implement proto encoding for START_SELECT_ROOMS_CLEAN
            await self.send_command({self.dps_map["PLAY_PAUSE"]: True})
        else:
            if self.device_model in EUFY_CLEAN_X_SERIES:
                await self.send_command({self.dps_map["WORK_MODE"]: EUFY_CLEAN_WORK_MODE["SMALL_ROOM"]})
            else:
                await self.send_command({self.dps_map["WORK_MODE"]: EUFY_CLEAN_WORK_MODE["ROOM"]})
            await self.play()

    async def send_command(self, data: Dict[str, Any]) -> None:
        """Send command to device."""
        raise NotImplementedError("Method not implemented")
