"""Data update coordinator for Eufy Clean."""
from datetime import timedelta
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EufyCleanApi

_LOGGER = logging.getLogger(__name__)

class EufyCleanDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: EufyCleanApi) -> None:
        """Initialize."""
        self.api = api
        self.platforms: list[str] = []

        super().__init__(
            hass,
            _LOGGER,
            name="Eufy Clean",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            devices = await self.api.get_all_devices()
            return {"devices": devices}
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
