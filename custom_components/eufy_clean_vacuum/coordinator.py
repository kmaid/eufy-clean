"""Data update coordinator for Eufy Clean Vacuum."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EufyCleanApi
from .proto.cloud import work_status_pb2
from .utils import decode_dps_protos

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)

class EufyCleanDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: EufyCleanApi) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Eufy Clean Vacuum",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self._data: Dict[str, Any] = {}

    async def async_setup(self) -> None:
        """Set up the coordinator."""
        _LOGGER.debug("Setting up coordinator")
        try:
            await self.api.async_setup()
            _LOGGER.debug("API setup completed successfully")
        except Exception as err:
            _LOGGER.error("Error setting up API: %s", err)
            raise UpdateFailed(f"Error setting up API: {err}") from err

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            # Get device list and states
            devices = await self.api.async_get_devices()

            # Decode protobuf values in device data
            for device in devices:
                if 'dps' in device:
                    device['decoded_dps'] = await decode_dps_protos(device['dps'])

            _LOGGER.debug("Got device list with decoded values: %s", devices)

            # Update our stored data
            self._data = {"devices": devices}
            return self._data

        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
