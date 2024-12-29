"""Support for Eufy Clean vacuum robots."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from eufy_clean import EufyClean

from .const import (
    DOMAIN,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FEATURES = (
    VacuumEntityFeature.START |
    VacuumEntityFeature.STOP |
    VacuumEntityFeature.RETURN_HOME |
    VacuumEntityFeature.BATTERY |
    VacuumEntityFeature.STATUS |
    VacuumEntityFeature.STATE |
    VacuumEntityFeature.PAUSE
)

# Map Eufy states to Home Assistant states
STATE_MAP = {
    'RUNNING': STATE_CLEANING,
    'CHARGING': STATE_DOCKED,
    'RECHARGE': STATE_RETURNING,
    'STANDBY': STATE_IDLE,
    'PAUSE': STATE_PAUSED,
    'ERROR': STATE_ERROR,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy Clean vacuum robots."""
    api: EufyClean = hass.data[DOMAIN][entry.entry_id]

    # Get the list of devices
    devices = await api.get_mqtt_devices()
    entities = []

    for device in devices:
        entities.append(EufyCleanVacuum(api, device))

    async_add_entities(entities, True)


class EufyCleanVacuum(StateVacuumEntity):
    """Eufy Clean Vacuum robot."""

    _attr_supported_features = SUPPORTED_FEATURES

    def __init__(self, api: EufyClean, device: dict) -> None:
        """Initialize the vacuum."""
        self._api = api
        self._device = device
        self._attr_unique_id = device.get("device_sn")
        self._attr_name = device.get("device_name", "Eufy Clean Vacuum")
        self._attr_state = None
        self._attr_battery_level = None
        self._attr_available = True
        self._attr_status = STATE_IDLE
        self._error_code = None

    @property
    def state(self) -> str | None:
        """Return the state of the vacuum."""
        return self._attr_state

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum."""
        return self._attr_battery_level

    @property
    def status(self) -> str:
        """Return the status of the vacuum."""
        return self._attr_status

    @property
    def error(self) -> str | None:
        """Return any error message."""
        return self._error_code

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        try:
            await self._api.send_command(self._device["device_sn"], {
                "command": "START_CLEANING",
            })
            self._attr_state = STATE_CLEANING
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to start cleaning: %s", err)

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        try:
            await self._api.send_command(self._device["device_sn"], {
                "command": "PAUSE_CLEANING",
            })
            self._attr_state = STATE_PAUSED
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to pause cleaning: %s", err)

    async def async_stop(self, **kwargs: Any) -> None:
        """Stop the vacuum cleaner."""
        try:
            await self._api.send_command(self._device["device_sn"], {
                "command": "STOP_CLEANING",
            })
            self._attr_state = STATE_IDLE
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to stop cleaning: %s", err)

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock."""
        try:
            await self._api.send_command(self._device["device_sn"], {
                "command": "RETURN_TO_BASE",
            })
            self._attr_state = STATE_RETURNING
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to return to base: %s", err)

    async def async_update(self) -> None:
        """Update the vacuum's status."""
        try:
            # Get the latest device status
            device = await self._api.get_device_status(self._device["device_sn"])
            if not device:
                self._attr_available = False
                return

            self._attr_available = True

            # Update state
            raw_state = device.get("state", "STANDBY")
            self._attr_state = STATE_MAP.get(raw_state, STATE_IDLE)

            # Update battery level
            self._attr_battery_level = device.get("battery_level")

            # Update status message
            self._attr_status = device.get("status_message", "")

            # Update error state
            error_code = device.get("error_code")
            if error_code:
                self._error_code = f"Error code: {error_code}"
                self._attr_state = STATE_ERROR
            else:
                self._error_code = None

        except Exception as err:
            _LOGGER.error("Failed to update Eufy Clean vacuum: %s", err)
            self._attr_available = False
