"""Support for Eufy Clean vacuums."""
from __future__ import annotations

import logging
from typing import Any

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

    # Docked/Charging states
    "charging": STATE_DOCKED,
    "recharge": STATE_DOCKED,
    "completed": STATE_DOCKED,
    "standby": STATE_DOCKED,
    "stand_by": STATE_DOCKED,

    # Idle/Sleeping states
    "sleeping": STATE_IDLE,
    "sleep": STATE_IDLE,

    # Error states
    "fault": STATE_ERROR,

    # Returning states
    "go_home": STATE_RETURNING,
    "recharge_needed": STATE_RETURNING,

    # Paused states
    "pause": STATE_PAUSED,
    "paused": STATE_PAUSED,
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

    _LOGGER.debug("Performing initial data refresh")
    await coordinator.async_config_entry_first_refresh()

    _LOGGER.debug("Getting device list")
    devices = await api.get_all_devices()
    _LOGGER.info("Found %d devices during setup", len(devices))

    entities = []

    for device in devices:
        # Handle both MQTT and cloud devices
        device_id = device.get("device_sn")
        device_model = device.get("deviceModel", "")
        device_name = device.get("deviceName", "")

        if not device_id:
            _LOGGER.warning("Device without ID found during setup: %s", device)
            continue

        _LOGGER.info(
            "Setting up vacuum entity - ID: %s, Name: %s, Model: %s",
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

        # Set up MQTT connection if available
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

    _LOGGER.info("Adding %d vacuum entities to Home Assistant", len(entities))
    async_add_entities(entities)

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
        self._attr_unique_id = f"eufy_clean_{device_id}"
        _LOGGER.debug(
            "Initialized vacuum entity - ID: %s, Name: %s, Unique ID: %s",
            device_id,
            name,
            self._attr_unique_id
        )

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum cleaner."""
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})
        level = device_data.get("battery_level")
        _LOGGER.debug("Device %s battery level: %s", self._device_id, level)
        return level

    @property
    def state(self) -> str | None:
        """Return the state of the vacuum cleaner."""
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})
        raw_state = str(device_data.get("state", "unknown")).lower()

        # Map the raw state to Home Assistant state
        ha_state = EUFY_TO_HA_STATE.get(raw_state)

        if not ha_state:
            _LOGGER.warning(
                "Unknown state received for device %s - Raw State: '%s', Full Device Data: %s",
                self._device_id,
                raw_state,
                device_data
            )
        else:
            _LOGGER.debug(
                "Device %s state: raw=%s, mapped=%s",
                self._device_id,
                raw_state,
                ha_state
            )

        return ha_state or "unknown"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})
        is_available = device_data.get("is_online", False)
        _LOGGER.debug("Device %s availability: %s", self._device_id, is_available)
        return is_available

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info."""
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})
        return {
            "identifiers": {("eufy_clean", self._device_id)},
            "name": device_data.get("name", self._attr_name),
            "model": device_data.get("model", "Unknown"),
            "manufacturer": "Eufy",
            "via_device": ("eufy_clean", "hub"),
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        device_data = self.coordinator.data.get("devices", {}).get(self._device_id, {})
        return {
            "device_type": device_data.get("type", "unknown"),
            "is_online": device_data.get("is_online", False),
            "raw_state": device_data.get("raw_state", {}),
            "error_code": device_data.get("error_code", 0),
            "work_status": device_data.get("state", "unknown"),
        }

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        _LOGGER.info("Starting cleaning for device %s", self._device_id)
        await self._shared_connect.play()
        await self.coordinator.async_request_refresh()

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        _LOGGER.info("Pausing cleaning for device %s", self._device_id)
        await self._shared_connect.pause()
        await self.coordinator.async_request_refresh()

    async def async_stop(self, **kwargs: Any) -> None:
        """Stop the cleaning task."""
        _LOGGER.info("Stopping cleaning for device %s", self._device_id)
        await self._shared_connect.stop()
        await self.coordinator.async_request_refresh()

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock."""
        _LOGGER.info("Returning to base for device %s", self._device_id)
        await self._shared_connect.go_home()
        await self.coordinator.async_request_refresh()
