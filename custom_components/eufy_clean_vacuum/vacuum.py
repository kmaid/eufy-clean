"""Support for Eufy Clean vacuums."""
from __future__ import annotations

import logging
from typing import Any, Dict

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EufyCleanApi
from .coordinator import EufyCleanDataUpdateCoordinator
from .shared_connect import SharedConnect
from .utils import get_multi_data

_LOGGER = logging.getLogger(__name__)

SUPPORT_EUFY_CLEAN = (
    VacuumEntityFeature.BATTERY |
    VacuumEntityFeature.PAUSE |
    VacuumEntityFeature.RETURN_HOME |
    VacuumEntityFeature.START |
    VacuumEntityFeature.STATE |
    VacuumEntityFeature.STOP
)

# Map Eufy states to Home Assistant states
EUFY_TO_HA_STATE = {
    # Running/Cleaning states
    "running": STATE_CLEANING,
    "cleaning": STATE_CLEANING,
    "spot": STATE_CLEANING,
    "cruising": STATE_CLEANING,
    "fast_mapping": STATE_CLEANING,
    "remote_ctrl": STATE_CLEANING,
    "auto": STATE_CLEANING,
    "room": STATE_CLEANING,
    "zone": STATE_CLEANING,
    "edge": STATE_CLEANING,
    "small_room": STATE_CLEANING,
    "global_cruise": STATE_CLEANING,
    "point_cruise": STATE_CLEANING,
    "zones_cruise": STATE_CLEANING,
    "scene_clean": STATE_CLEANING,
    "1": STATE_CLEANING,  # Novel API cleaning

    # Docked/Charging states
    "charging": STATE_DOCKED,
    "recharge": STATE_DOCKED,
    "completed": STATE_DOCKED,
    "standby": STATE_DOCKED,
    "stand_by": STATE_DOCKED,
    "2": STATE_DOCKED,  # Novel API charging
    "4": STATE_DOCKED,  # Novel API standby

    # Idle/Sleeping states
    "sleeping": STATE_IDLE,
    "sleep": STATE_IDLE,
    "stopped": STATE_IDLE,
    "no_sweep": STATE_IDLE,

    # Error states
    "fault": STATE_ERROR,
    "error": STATE_ERROR,

    # Returning states
    "go_home": STATE_RETURNING,
    "recharge_needed": STATE_RETURNING,
    "exploring_station": STATE_RETURNING,

    # Paused states
    "pause": STATE_PAUSED,
    "paused": STATE_PAUSED,
    "3": STATE_PAUSED,  # Novel API paused
}

# Additional attributes for more detailed status
EUFY_CLEAN_SPEED = {
    "no_suction": "No Suction",
    "standard": "Standard",
    "quiet": "Quiet",
    "turbo": "Turbo",
    "boost_iq": "Boost IQ",
    "max": "Max"
}

EUFY_CLEAN_MODE = {
    "auto": "Auto",
    "no_sweep": "No Sweep",
    "small_room": "Small Room",
    "room": "Room",
    "zone": "Zone",
    "edge": "Edge",
    "spot": "Spot"
}

EUFY_CLEAN_TYPE = {
    "sweep_and_mop": "Sweep and Mop",
    "sweep_only": "Sweep Only",
    "mop_only": "Mop Only"
}

EUFY_MOP_MODE = {
    "high": "High",
    "medium": "Medium",
    "low": "Low"
}

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

        if entities:
            _LOGGER.info("Adding %d unique vacuum entities to Home Assistant", len(entities))
            async_add_entities(entities)
        else:
            _LOGGER.warning("No vacuum entities to add to Home Assistant")

    except Exception as err:
        _LOGGER.error("Error setting up vacuum platform: %s", err)
        raise

class EufyCleanVacuum(CoordinatorEntity[EufyCleanDataUpdateCoordinator], StateVacuumEntity):
    """Eufy Clean Vacuum."""

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
        self._attr_name = name
        self._shared_connect = shared_connect
        self._attr_supported_features = SUPPORT_EUFY_CLEAN
        self._attr_unique_id = f"{device_id}"
        _LOGGER.debug(
            "Initialized vacuum entity - ID: %s, Name: %s, Unique ID: %s",
            device_id,
            name,
            self._attr_unique_id
        )

    @property
    def _device(self) -> Dict[str, Any]:
        """Get current device data."""
        return next(
            (d for d in self.coordinator.data.get("devices", [])
             if d.get("device_sn") == self._device_id),
            {}
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        dps = self._device.get("dps", {})
        attributes = {
            "battery_level": self._device.get("battery_level", 0),
            "is_online": self._device.get("is_online", False),
            "raw_state": self._device.get("raw_state", {}),
            "dps": dps,
            "is_novel_api": self._device.get("is_novel_api", False),
            "device_model": self._device.get("deviceModel", ""),
            "device_type": self._device.get("type", "unknown"),
        }

        # Add clean speed
        if self._device.get("is_novel_api"):
            if "158" in dps:  # Novel API clean speed
                speed_index = dps["158"]
                speeds = list(EUFY_CLEAN_SPEED.values())
                if 0 <= speed_index < len(speeds):
                    attributes["clean_speed"] = speeds[speed_index]
        elif "102" in dps:  # Legacy API clean speed
            speed = str(dps["102"]).lower()
            attributes["clean_speed"] = EUFY_CLEAN_SPEED.get(speed, speed)

        # Add work mode
        if self._device.get("is_novel_api"):
            if "153" in dps:  # Novel API work mode
                try:
                    mode_data = dps["153"]
                    if isinstance(mode_data, dict) and "Mode" in mode_data:
                        mode = str(mode_data["Mode"]).lower()
                        attributes["work_mode"] = EUFY_CLEAN_MODE.get(mode, mode)
                except Exception:
                    pass
        elif "5" in dps:  # Legacy API work mode
            mode = str(dps["5"]).lower()
            attributes["work_mode"] = EUFY_CLEAN_MODE.get(mode, mode)

        # Add clean type and mop mode for novel API
        if self._device.get("is_novel_api") and "154" in dps:
            try:
                clean_params = dps["154"]
                if isinstance(clean_params, dict):
                    if "cleanType" in clean_params:
                        clean_type = str(clean_params["cleanType"]).lower()
                        attributes["clean_type"] = EUFY_CLEAN_TYPE.get(clean_type, clean_type)
                    if "mopMode" in clean_params:
                        mop_mode = str(clean_params["mopMode"]).lower()
                        attributes["mop_mode"] = EUFY_MOP_MODE.get(mop_mode, mop_mode)
            except Exception:
                pass

        # Add error code if present
        if self._device.get("is_novel_api"):
            if "177" in dps:  # Novel API error code
                attributes["error_code"] = dps["177"]
        elif "106" in dps:  # Legacy API error code
            attributes["error_code"] = dps["106"]

        return attributes

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum cleaner."""
        return self._device.get("battery_level")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.get("is_online", False)

    @property
    def state(self) -> str:
        """Return the state of the vacuum cleaner."""
        try:
            device = next(
                (d for d in self.coordinator.data.get("devices", [])
                 if d.get("device_sn") == self._device_id),
                {}
            )
            dps = device.get("dps", {})

            # Check if device is offline
            if not device.get("is_online", True):
                return "unavailable"

            # Get state from DPS
            if "153" in dps:  # Novel API state
                work_status = dps["153"]
                if isinstance(work_status, str) and work_status.startswith("Ch"):
                    # We can't use await here, so we'll just use the raw value
                    if str(work_status) == "1":
                        return "cleaning"
                    elif str(work_status) == "2":
                        return "returning"
                    elif str(work_status) == "3":
                        return "paused"
                    elif str(work_status) == "4":
                        return "idle"
                elif isinstance(work_status, (int, str)):
                    if str(work_status) == "1":
                        return "cleaning"
                    elif str(work_status) == "2":
                        return "returning"
                    elif str(work_status) == "3":
                        return "paused"
                    elif str(work_status) == "4":
                        return "idle"

            elif "15" in dps:  # Legacy API state
                state = str(dps["15"]).lower()
                if state in ["cleaning", "returning", "paused", "idle"]:
                    return state

            # If we get here, we couldn't determine the state
            _LOGGER.warning(
                "Unknown state received for device %s - Raw State: '%s', Full Device Data: %s",
                self._device_id,
                device.get("state", "unknown"),
                device
            )
            return "unknown"

        except Exception as err:
            _LOGGER.error("Error getting vacuum state: %s", err)
            return "error"

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        await self.coordinator.api.send_command(self._device_id, {"play": True})

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        await self.coordinator.api.send_command(self._device_id, {"play": False})

    async def async_stop(self) -> None:
        """Stop the cleaning task."""
        await self.coordinator.api.send_command(self._device_id, {"play": False})

    async def async_return_to_base(self) -> None:
        """Set the vacuum cleaner to return to the dock."""
        await self.coordinator.api.send_command(self._device_id, {"go_home": True})

