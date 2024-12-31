"""The Eufy Clean Vacuum integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from .api import EufyCleanApi
from .base import Base
from .shared_connect import SharedConnect

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.VACUUM]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy Clean Vacuum from a config entry."""
    # Get the Home Assistant locale
    locale = hass.config.language or "en"

    api = EufyCleanApi(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        locale=locale,
    )

    try:
        await api.init()
    except Exception as err:
        _LOGGER.error("Error setting up Eufy Clean integration: %s", err)
        return False

    hass.data.setdefault("eufy_clean_vacuum", {})[entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        api = hass.data["eufy_clean_vacuum"].pop(entry.entry_id)
        await api.close()

    return unload_ok
