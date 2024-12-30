"""The Eufy Clean Vacuum integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .eufy_clean import EufyClean

_LOGGER = logging.getLogger(__name__)

DOMAIN = "eufy_clean_vacuum"
PLATFORMS = [Platform.VACUUM]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Eufy Clean Vacuum component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy Clean Vacuum from a config entry."""
    try:
        # Create API instance
        api = EufyClean(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
        )

        # Test the API connection
        await api.init()

        # Store API instance
        hass.data[DOMAIN][entry.entry_id] = api

        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True

    except Exception as err:
        _LOGGER.error("Failed to connect to Eufy Clean API: %s", err)
        # Don't raise ConfigEntryNotReady here, as it might prevent reloading
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN].pop(entry.entry_id)
        await api.close()

    return unload_ok
