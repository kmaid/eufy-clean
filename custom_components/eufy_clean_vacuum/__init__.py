"""The Eufy Clean Vacuum integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .eufy_clean import EufyClean

_LOGGER = logging.getLogger(__name__)

DOMAIN = "eufy_clean_vacuum"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy Clean Vacuum from a config entry."""
    try:
        api = EufyClean(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
        )
        await api.init()
    except Exception as err:
        _LOGGER.error("Failed to connect to Eufy Clean API: %s", err)
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
