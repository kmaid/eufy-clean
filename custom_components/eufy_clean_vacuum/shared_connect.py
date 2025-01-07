"""Shared connection handler."""
import logging
from typing import Any, Dict, Optional
import time

from .base import Base
from .utils import encode
from .const import EUFY_CLEAN_X_SERIES

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
        _LOGGER.info("Initialized SharedConnect - Device ID: %s, Model: %s, Debug: %s",
                    self.device_id, self.device_model, self.debug)
        _LOGGER.debug("Full config: %s", config)

    async def set_mqtt_connect(self, mqtt_connect) -> None:
        """Set MQTT connection."""
        self.mqtt_connect = mqtt_connect
        _LOGGER.info("MQTT connection set for device %s", self.device_id)
        # Check API type immediately after MQTT connection is set
        _LOGGER.debug("Initial DPS map before API check: %s", self.dps_map)
        if hasattr(mqtt_connect, 'devices'):
            device = next((d for d in mqtt_connect.devices if d.get('device_sn') == self.device_id), None)
            if device:
                _LOGGER.debug("Found device in MQTT devices: %s", device)
                await self.check_api_type(device.get('dps', {}))
            else:
                _LOGGER.warning("Device %s not found in MQTT devices", self.device_id)

    async def check_api_type(self, dps: Dict[str, Any]) -> None:
        """Check API type."""
        try:
            _LOGGER.debug("=== Starting API Type Check ===")
            _LOGGER.debug("Input DPS data: %s", dps)
            _LOGGER.debug("Current device model: %s", self.device_model)
            _LOGGER.debug("Current DPS map: %s", self.dps_map)
            _LOGGER.debug("Current API type: %s", "Novel" if self.novel_api else "Legacy")
            _LOGGER.debug("Novel DPS map values: %s", list(self.novel_dps_map.values()))

            # First check if this is a known novel API model
            model_code = self.device_model[:5] if self.device_model else ""
            _LOGGER.debug("Extracted model code: %s", model_code)
            _LOGGER.debug("X-series models: %s", EUFY_CLEAN_X_SERIES)
            is_novel_model = model_code in EUFY_CLEAN_X_SERIES
            _LOGGER.debug("Is novel model? %s", is_novel_model)

            if is_novel_model:
                _LOGGER.info("Novel API detected based on model %s (code: %s)", self.device_model, model_code)
                await self.set_api_types(True)
                return

            # If not a known model, check DPS keys
            matching_keys = [k for k in dps.keys() if k in self.novel_dps_map.values()]
            _LOGGER.debug("DPS keys in input: %s", list(dps.keys()))
            _LOGGER.debug("Matching novel DPS keys: %s", matching_keys)

            if not self.novel_api and matching_keys:
                _LOGGER.info("Novel API detected - Matching DPS keys: %s", matching_keys)
                await self.set_api_types(True)
            else:
                _LOGGER.info("Legacy API detected - No matching novel DPS keys found")
                _LOGGER.debug("DPS keys: %s", list(dps.keys()))
                await self.set_api_types(False)

            _LOGGER.debug("=== API Type Check Complete ===")
            _LOGGER.debug("Final API type: %s", "Novel" if self.novel_api else "Legacy")
            _LOGGER.debug("Final DPS map: %s", self.dps_map)

        except Exception as err:
            _LOGGER.error("Error checking API type: %s", err, exc_info=True)
            _LOGGER.debug("Error context - Device ID: %s, Model: %s, DPS: %s",
                         self.device_id, self.device_model, dps)

    async def set_api_types(self, novel_api: bool) -> None:
        """Set API types."""
        old_api = "Novel" if self.novel_api else "Legacy"
        new_api = "Novel" if novel_api else "Legacy"
        _LOGGER.info("Switching API type from %s to %s for device %s", old_api, new_api, self.device_id)
        _LOGGER.debug("Old DPS map: %s", self.dps_map)

        self.novel_api = novel_api
        self.dps_map = self.novel_dps_map if novel_api else self.legacy_dps_map
        self.robovac_data = self.dps_map.copy()

        _LOGGER.debug("New DPS map: %s", self.dps_map)
        _LOGGER.debug("New robovac data: %s", self.robovac_data)

    def map_data(self, dps: Dict[str, Any]) -> None:
        """Map DPS data."""
        if not dps:
            _LOGGER.debug("No DPS data to map")
            return

        _LOGGER.debug("Mapping DPS data: %s", dps)
        for key, value in dps.items():
            mapped_keys = [k for k, v in self.dps_map.items() if v == key]
            for mapped_key in mapped_keys:
                old_value = self.robovac_data.get(mapped_key)
                self.robovac_data[mapped_key] = value
                if old_value != value:
                    _LOGGER.debug("Updated %s: %s -> %s", mapped_key, old_value, value)

        if self.debug:
            _LOGGER.debug("Mapped data: %s", self.robovac_data)

    async def get_robovac_data(self) -> Dict[str, Any]:
        """Get robovac data."""
        return self.robovac_data

    async def get_battery_level(self) -> Optional[int]:
        """Get battery level."""
        level = self.robovac_data.get("BATTERY_LEVEL")
        _LOGGER.debug("Battery level: %s", level)
        return level

    async def get_work_status(self) -> str:
        """Get work status."""
        status = str(self.robovac_data.get("WORK_STATUS", "CHARGING")).lower()
        _LOGGER.debug("Work status: %s", status)
        return status

    async def get_error_code(self) -> Optional[int]:
        """Get error code."""
        code = self.robovac_data.get("ERROR_CODE", 0)
        if code != 0:
            _LOGGER.warning("Error code detected: %s", code)
        return code

    async def play(self) -> None:
        """Start or resume cleaning."""
        _LOGGER.info("Play command requested - API type: %s", "Novel" if self.novel_api else "Legacy")
        if self.novel_api:
            try:
                _LOGGER.debug("Encoding START_AUTO_CLEAN command for novel API")
                value = await encode("custom_components.eufy_clean_vacuum.proto.cloud.control_pb2", "ModeCtrlRequest", {
                    "method": "START_AUTO_CLEAN"
                })
                _LOGGER.debug("Encoded command value: %s", value)
                await self.send_command({self.dps_map["PLAY_PAUSE"]: value})
            except Exception as err:
                _LOGGER.error("Failed to encode START_AUTO_CLEAN command: %s", err, exc_info=True)
                return
        else:
            await self.send_command({self.dps_map["PLAY_PAUSE"]: True})

    async def pause(self) -> None:
        """Pause cleaning."""
        _LOGGER.info("Pause command requested - API type: %s", "Novel" if self.novel_api else "Legacy")
        if self.novel_api:
            try:
                _LOGGER.debug("Encoding PAUSE_CLEAN command for novel API")
                value = await encode("custom_components.eufy_clean_vacuum.proto.cloud.control_pb2", "ModeCtrlRequest", {
                    "method": "PAUSE_CLEAN"
                })
                _LOGGER.debug("Encoded command value: %s", value)
                await self.send_command({self.dps_map["PLAY_PAUSE"]: value})
            except Exception as err:
                _LOGGER.error("Failed to encode PAUSE_CLEAN command: %s", err, exc_info=True)
                return
        else:
            await self.send_command({self.dps_map["PLAY_PAUSE"]: False})

    async def stop(self) -> None:
        """Stop cleaning."""
        _LOGGER.info("Stop command requested - API type: %s", "Novel" if self.novel_api else "Legacy")
        if self.novel_api:
            try:
                _LOGGER.debug("Encoding STOP_CLEAN command for novel API")
                value = await encode("custom_components.eufy_clean_vacuum.proto.cloud.control_pb2", "ModeCtrlRequest", {
                    "method": "STOP_CLEAN"
                })
                _LOGGER.debug("Encoded command value: %s", value)
                await self.send_command({self.dps_map["PLAY_PAUSE"]: value})
            except Exception as err:
                _LOGGER.error("Failed to encode STOP_CLEAN command: %s", err, exc_info=True)
                return
        else:
            await self.send_command({self.dps_map["PLAY_PAUSE"]: False})

    async def go_home(self) -> None:
        """Return to dock."""
        _LOGGER.info("Go home command requested - API type: %s", "Novel" if self.novel_api else "Legacy")
        if self.novel_api:
            try:
                _LOGGER.debug("Encoding START_GOHOME command for novel API")
                value = await encode("custom_components.eufy_clean_vacuum.proto.cloud.control_pb2", "ModeCtrlRequest", {
                    "method": "START_GOHOME"
                })
                _LOGGER.debug("Encoded command value: %s", value)
                await self.send_command({self.dps_map["PLAY_PAUSE"]: value})
            except Exception as err:
                _LOGGER.error("Failed to encode START_GOHOME command: %s", err, exc_info=True)
                return
        else:
            await self.send_command({self.dps_map["GO_HOME"]: True})

    async def send_command(self, dps: Dict[str, Any]) -> None:
        """Send command to device."""
        if not self.mqtt_connect:
            _LOGGER.error("No MQTT connection available for device %s", self.device_id)
            return

        try:
            _LOGGER.info("Sending command to device %s", self.device_id)
            _LOGGER.debug("Command DPS data: %s", dps)
            _LOGGER.debug("Current DPS map: %s", self.dps_map)
            _LOGGER.debug("API type: %s", "Novel" if self.novel_api else "Legacy")

            await self.mqtt_connect.send_command(self.device_id, dps)
            _LOGGER.info("Command sent successfully")
        except Exception as err:
            _LOGGER.error("Error sending command to device %s: %s", self.device_id, err, exc_info=True)
            _LOGGER.debug("Failed command DPS: %s", dps)
