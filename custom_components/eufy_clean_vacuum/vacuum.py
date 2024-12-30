"""Support for Eufy Clean vacuums."""
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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy Clean vacuum from a config entry."""
    api: EufyCleanApi = hass.data["eufy_clean_vacuum"][entry.entry_id]
    coordinator = EufyCleanDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    devices = await api.get_all_devices()
    entities = []

    for device in devices:
        # Handle both MQTT and cloud devices
        device_id = device.get("device_sn") or device.get("devId")
        device_model = device.get("deviceModel", "")
        device_name = device.get("deviceName", "")

        if not device_id:
            _LOGGER.warning("Device without ID found: %s", device)
            continue

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

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the vacuum cleaner."""
        return self.coordinator.data.get("devices", {}).get(self._device_id, {}).get("battery_level")

    @property
    def state(self) -> str | None:
        """Return the state of the vacuum cleaner."""
        return self.coordinator.data.get("devices", {}).get(self._device_id, {}).get("state", "unknown")

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        await self._shared_connect.play()
        await self.coordinator.async_request_refresh()

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        await self._shared_connect.pause()
        await self.coordinator.async_request_refresh()

    async def async_stop(self, **kwargs: Any) -> None:
        """Stop the cleaning task."""
        await self._shared_connect.stop()
        await self.coordinator.async_request_refresh()

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Set the vacuum cleaner to return to the dock."""
        await self._shared_connect.go_home()
        await self.coordinator.async_request_refresh()
