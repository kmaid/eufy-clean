"""Support for Eufy Clean vacuums."""
from __future__ import annotations

import logging
import base64
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
from .utils import decode_protobuf
from .proto.cloud import work_status_pb2
from .constants import EUFY_CLEAN_CONTROL

_LOGGER = logging.getLogger(__name__)

SUPPORT_EUFY_CLEAN = (
    VacuumEntityFeature.BATTERY |
    VacuumEntityFeature.PAUSE |
    VacuumEntityFeature.RETURN_HOME |
    VacuumEntityFeature.START |
    VacuumEntityFeature.STATE |
    VacuumEntityFeature.STOP
)

# Map Eufy protobuf states to Home Assistant states
PROTO_STATE_MAP = {
    "standby": STATE_IDLE,
    "sleep": STATE_IDLE,
    "fault": STATE_ERROR,
    "charging": STATE_DOCKED,
    "fast_mapping": STATE_CLEANING,
    "cleaning": STATE_CLEANING,
    "remote_ctrl": STATE_CLEANING,
    "go_home": STATE_RETURNING,
    "cruisiing": STATE_CLEANING,
}

# Map Eufy states to Home Assistant states (for legacy API)
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
        attributes = {}

        # Add raw DPS data for debugging
        attributes["raw_dps"] = dps

        # Add battery level
        if "163" in dps:
            attributes["battery_level"] = dps["163"]

        # Add cleaning state details
        if "151" in dps:
            attributes["cleaning_enabled"] = dps["151"]
        if "156" in dps:
            attributes["docked"] = dps["156"]

        return attributes

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

    @property
    def state(self) -> str:
        """Return the state of the vacuum cleaner."""
        device = self._device
        if not device:
            return STATE_ERROR

        dps = device.get("dps", {})

        # Get state from DPS 158 (main state)
        state = dps.get("158", "").lower()

        # Check if the vacuum is docked/charging
        if dps.get("156", False):  # DPS 156 indicates if docked
            return STATE_DOCKED

        # If not docked, then check the main state
        if state == "1":
            if dps.get("151", False):  # If cleaning enabled
                return STATE_CLEANING
            return STATE_IDLE
        elif state == "2":
            return STATE_RETURNING
        elif state == "3":
            return STATE_PAUSED
        elif state == "4":
            return STATE_IDLE

        # Fallback to legacy state mapping
        return EUFY_TO_HA_STATE.get(state, STATE_ERROR)

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        await self._shared_connect.send_command(self._device_id, {
            "method": EUFY_CLEAN_CONTROL["RESUME_TASK"]
        })

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        await self._shared_connect.send_command(self._device_id, {
            "method": EUFY_CLEAN_CONTROL["PAUSE_TASK"]
        })

    async def async_stop(self) -> None:
        """Stop the cleaning task."""
        await self._shared_connect.send_command(self._device_id, {
            "method": EUFY_CLEAN_CONTROL["STOP_TASK"]
        })

    async def async_return_to_base(self) -> None:
        """Set the vacuum cleaner to return to the dock."""
        await self._shared_connect.send_command(self._device_id, {
            "method": EUFY_CLEAN_CONTROL["START_GOHOME"]
        })

