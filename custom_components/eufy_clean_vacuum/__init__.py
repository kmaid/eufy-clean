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
    hass.data.setdefault(DOMAIN, {})

    try:
        api = EufyClean(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
        )
        await api.init()
        hass.data[DOMAIN][entry.entry_id] = api
    except Exception as err:
        _LOGGER.error("Failed to connect to Eufy Clean API: %s", err)
        raise ConfigEntryNotReady from err

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN].pop(entry.entry_id)
        await api.close()
    return True
