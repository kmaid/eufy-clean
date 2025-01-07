"""Support for Eufy Clean vacuums."""
from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    VacuumActivity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EufyCleanApi
from .coordinator import EufyCleanDataUpdateCoordinator
from .shared_connect import SharedConnect
from .utils import decode_protobuf
from .const import (
    EUFY_CLEAN_CONTROL,
    EUFY_CLEAN_GET_CLEAN_SPEED,
    EUFY_CLEAN_WORK_STATUS,
    EUFY_CLEAN_WORK_MODE,
    EUFY_CLEAN_ERROR_CODES,
    EUFY_CLEAN_TYPE,
    EUFY_MOP_MODE,
    PROTO_STATE_MAP,
    EUFY_TO_HA_STATE,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_EUFY_CLEAN = (
    VacuumEntityFeature.BATTERY |
    VacuumEntityFeature.PAUSE |
    VacuumEntityFeature.RETURN_HOME |
    VacuumEntityFeature.START |
    VacuumEntityFeature.STATUS |
    VacuumEntityFeature.STOP |
    VacuumEntityFeature.SEND_COMMAND
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy Clean vacuum from a config entry."""
    _LOGGER.info("Setting up Eufy Clean vacuum integration")

    api: EufyCleanApi = hass.data["eufy_clean_vacuum"][entry.entry_id]
    coordinator = EufyCleanDataUpdateCoordinator(hass, api)

    _LOGGER.debug("Setting up coordinator")
    try:
        # First set up the coordinator
        await coordinator.async_setup()

        # Then perform initial refresh
        await coordinator.async_config_entry_first_refresh()

        if not coordinator.data:
            _LOGGER.error("Failed to get initial data from coordinator")
            return

        _LOGGER.debug("Getting device list")
        devices = coordinator.data.get("devices", [])
        _LOGGER.info("Found %d devices during setup", len(devices))

        if not devices:
            _LOGGER.warning("No devices found during setup")
            return

        # Track devices we've already added to avoid duplicates
        added_devices = set()
        entities = []

        # First add MQTT devices
        for device in devices:
            if device.get("type") != "mqtt":
                continue

            device_id = device.get("device_sn")
            if not device_id:
                _LOGGER.warning("Device without ID found during setup: %s", device)
                continue

            if device_id in added_devices:
                _LOGGER.debug("Device %s already added, skipping duplicate", device_id)
                continue

            device_model = device.get("deviceModel", "")
            device_name = device.get("deviceName", "")

            _LOGGER.info(
                "Setting up MQTT vacuum entity - ID: %s, Name: %s, Model: %s",
                device_id,
                device_name or "Unknown",
                device_model or "Unknown"
            )

            config = {
                "device_id": device_id,
                "device_model": device_model,
                "debug": False,
            }
            shared_connect = SharedConnect(config)

            # Set up MQTT connection
            if api.login.mqtt_connect:
                _LOGGER.info("Setting up MQTT connection for device %s", device_id)
                await shared_connect.set_mqtt_connect(api.login.mqtt_connect)
            else:
                _LOGGER.warning("No MQTT connection available for device %s", device_id)

            entities.append(
                EufyCleanVacuum(
                    coordinator,
                    device_id,
                    device_name,
                    shared_connect,
                )
            )
            added_devices.add(device_id)

        # Then add cloud devices that aren't already added via MQTT
        for device in devices:
            if device.get("type") == "mqtt":
                continue

            device_id = device.get("device_sn")
            if not device_id:
                _LOGGER.warning("Device without ID found during setup: %s", device)
                continue

            if device_id in added_devices:
                _LOGGER.debug("Device %s already added via MQTT, skipping cloud version", device_id)
                continue

            device_model = device.get("deviceModel", "")
            device_name = device.get("deviceName", "")

            _LOGGER.info(
                "Setting up cloud vacuum entity - ID: %s, Name: %s, Model: %s",
                device_id,
                device_name or "Unknown",
                device_model or "Unknown"
            )

            config = {
                "device_id": device_id,
                "device_model": device_model,
                "debug": False,
            }
            shared_connect = SharedConnect(config)

            entities.append(
                EufyCleanVacuum(
                    coordinator,
                    device_id,
                    device_name,
                    shared_connect,
                )
            )
            added_devices.add(device_id)

        _LOGGER.info("Adding %d unique vacuum entities to Home Assistant", len(entities))
        async_add_entities(entities)

    except Exception as err:
        _LOGGER.error("Error setting up Eufy Clean vacuum integration: %s", err)
        raise

class EufyCleanVacuum(CoordinatorEntity[EufyCleanDataUpdateCoordinator], StateVacuumEntity):
    """Eufy Clean Vacuum Entity."""

    def __init__(
        self,
        coordinator: EufyCleanDataUpdateCoordinator,
        device_id: str,
        name: str,
        shared_connect: SharedConnect,
    ) -> None:
        """Initialize the vacuum."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._name = name
        self._shared_connect = shared_connect
        self._attr_supported_features = SUPPORT_EUFY_CLEAN
        self._attr_unique_id = device_id

    @property
    def _device(self) -> Dict[str, Any]:
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return {}
        devices = self.coordinator.data.get("devices", [])
        return next(
            (d for d in devices if d.get("device_sn") == self._device_id),
            {}
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        device = self._device
        if not device:
            return {}

        dps = device.get("dps", {})
        decoded_dps = device.get("decoded_dps", {})
        attributes = {}

        # Add device info from DPS 169
        if "169" in decoded_dps:
            device_info = decoded_dps["169"]
            if isinstance(device_info, dict):
                attributes.update({
                    "firmware_version": device_info.get("software"),
                    "hardware_version": device_info.get("hardware"),
                    "wifi_ip": device_info.get("wifi_ip"),
                    "wifi_name": device_info.get("wifi_name"),
                    "mac_address": device_info.get("device_mac"),
                    "station_firmware": device_info.get("station", {}).get("software"),
                    "station_hardware": device_info.get("station", {}).get("hardware"),
                })

        # Add clean parameters from DPS 154
        if "154" in decoded_dps:
            clean_param = decoded_dps["154"]
            if isinstance(clean_param, dict):
                if "clean_type" in clean_param and clean_param["clean_type"] is not None:
                    clean_type = clean_param["clean_type"].get("value", "").lower()
                    attributes["clean_type"] = EUFY_CLEAN_TYPE.get(clean_type, clean_type)
                if "fan" in clean_param and clean_param["fan"] is not None:
                    fan_speed = clean_param["fan"].get("value", "").lower()
                    attributes["fan_speed"] = EUFY_CLEAN_GET_CLEAN_SPEED.get(fan_speed, fan_speed)
                if "mop_mode" in clean_param and clean_param["mop_mode"] is not None:
                    mop_mode = clean_param["mop_mode"].get("level", "").lower()
                    attributes["mop_mode"] = EUFY_MOP_MODE.get(mop_mode, mop_mode)

        # Add work status from DPS 157
        if "157" in decoded_dps:
            work_status = decoded_dps["157"]
            _LOGGER.debug("Work status from DPS 157: %s", work_status)
            if isinstance(work_status, dict):
                # Get mode and state
                mode = work_status.get("mode", {})
                state = work_status.get("state", "CHARGING")  # Default to CHARGING as per TypeScript
                _LOGGER.debug("Work status mode: %s, state: %s", mode, state)

                # Handle mode value which is a nested dict
                mode_value = mode.get("value", "") if isinstance(mode, dict) else str(mode)
                mode_value = mode_value.lower() if mode_value else "auto"  # Default to auto as per TypeScript

                # Handle state value
                state_value = state.lower() if state else "charging"  # Default to charging as per TypeScript

                attributes.update({
                    "cleaning_mode": EUFY_CLEAN_WORK_MODE.get(mode_value.upper(), mode_value),
                    "cleaning_state": EUFY_CLEAN_WORK_STATUS.get(state_value.upper(), state_value),
                })

                # Handle status flags based on state
                is_cleaning = state_value in ["running", "cleaning"]
                is_charging = state_value in ["charging", "completed"]
                is_returning = state_value in ["recharge", "recharge_needed", "go_home"]
                is_washing = state_value == "go_wash"
                is_mapping = state_value == "fast_mapping"

                attributes.update({
                    "is_charging": is_charging,
                    "is_cleaning": is_cleaning,
                    "is_returning_home": is_returning,
                    "is_washing": is_washing,
                    "is_mapping": is_mapping,
                })

        # Add cleaning statistics from DPS 177
        if "177" in decoded_dps:
            stats = decoded_dps["177"]
            if isinstance(stats, dict):
                attributes.update({
                    "total_cleaning_time": stats.get("total"),
                    "user_cleaning_time": stats.get("user_total"),
                })

        # Add consumable info from DPS 179
        if "179" in decoded_dps:
            consumable = decoded_dps["179"]
            if isinstance(consumable, dict):
                attributes["consumable_reset_types"] = consumable.get("reset_types", [])

        # Add scene info from DPS 180
        if "180" in decoded_dps:
            scene = decoded_dps["180"]
            if isinstance(scene, dict) and "scene" in scene:
                scene_info = scene["scene"].get("info", {})
                attributes.update({
                    "scene_name": scene_info.get("name"),
                    "scene_type": scene_info.get("type"),
                    "scene_estimate_time": scene_info.get("estimate_time"),
                })

        # Add basic status flags
        attributes.update({
            "is_docked": dps.get("156", False),
            "cleaning_enabled": dps.get("151", False),
            "auto_empty_enabled": dps.get("159", False),
            "auto_wash_enabled": dps.get("160", False),
        })

        # Add error information if present
        error_code = dps.get("161", 0)
        if error_code > 0:
            error_message = EUFY_CLEAN_ERROR_CODES.get(error_code, f"Unknown error {error_code}")
            attributes.update({
                "error_code": error_code,
                "error_message": error_message,
            })

        return attributes

    @property
    def activity(self) -> VacuumActivity:
        """Return the activity of the vacuum cleaner."""
        device = self._device
        if not device:
            return VacuumActivity.ERROR

        dps = device.get("dps", {})
        decoded_dps = device.get("decoded_dps", {})

        # Check for errors first
        if dps.get("161", 0) > 0:
            return VacuumActivity.ERROR

        # First check if we have decoded work status from DPS 157
        if "157" in decoded_dps:
            work_status = decoded_dps["157"]
            if isinstance(work_status, dict):
                # Check if docked/charging
                if dps.get("156", False):  # DPS 156 indicates if docked
                    if work_status.get("charging"):
                        return VacuumActivity.DOCKED
                    return VacuumActivity.IDLE

                # Get the main state
                state = work_status.get("state", "").lower()
                if state in PROTO_STATE_MAP:
                    return PROTO_STATE_MAP[state]

                # Check specific work modes
                if work_status.get("cleaning"):
                    return VacuumActivity.CLEANING
                if work_status.get("go_home"):
                    return VacuumActivity.RETURNING
                if work_status.get("go_wash"):
                    return VacuumActivity.RETURNING

        # Fallback to DPS 158 for legacy state handling
        state = dps.get("158", "").lower()
        return EUFY_TO_HA_STATE.get(state, VacuumActivity.ERROR)

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum cleaner."""
        device = self._device
        return device.get("dps", {}).get("163")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        device = self._device
        return bool(device.get("is_online", False))

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        value = True
        if self._shared_connect.novel_api:
            value = {
                "method": EUFY_CLEAN_CONTROL["RESUME_TASK"]
            }
        await self._shared_connect.send_command({
            self._shared_connect.dps_map["PLAY_PAUSE"]: value
        })

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        value = False
        if self._shared_connect.novel_api:
            value = {
                "method": EUFY_CLEAN_CONTROL["PAUSE_TASK"]
            }
        await self._shared_connect.send_command({
            self._shared_connect.dps_map["PLAY_PAUSE"]: value
        })

    async def async_stop(self) -> None:
        """Stop the cleaning task."""
        value = False
        if self._shared_connect.novel_api:
            value = {
                "method": EUFY_CLEAN_CONTROL["STOP_TASK"]
            }
        await self._shared_connect.send_command({
            self._shared_connect.dps_map["PLAY_PAUSE"]: value
        })

    async def async_return_to_base(self) -> None:
        """Set the vacuum cleaner to return to the dock."""
        if self._shared_connect.novel_api:
            value = {
                "method": EUFY_CLEAN_CONTROL["START_GOHOME"]
            }
            await self._shared_connect.send_command({
                self._shared_connect.dps_map["PLAY_PAUSE"]: value
            })
        else:
            await self._shared_connect.send_command({
                self._shared_connect.dps_map["GO_HOME"]: True
            })

    async def async_send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a command to the vacuum."""
        if params is None:
            params = {}

        if self._shared_connect.novel_api:
            value = {
                "method": command,
                **params
            }
            await self._shared_connect.send_command({
                self._shared_connect.dps_map["PLAY_PAUSE"]: value
            })
        else:
            await self._shared_connect.send_command({
                self._shared_connect.dps_map["PLAY_PAUSE"]: command,
                **params
            })

