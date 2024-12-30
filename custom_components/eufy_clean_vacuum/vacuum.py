"""Support for Eufy Clean vacuum cleaners."""
import logging

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Eufy Clean vacuum platform."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    # For now, just log that we're setting up the vacuum
    _LOGGER.debug("Setting up Eufy Clean vacuum platform")
    # We'll add actual vacuum entities later
