"""Config flow for Eufy Clean Vacuum integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .eufy_clean import EufyClean

_LOGGER = logging.getLogger(__name__)

DOMAIN = "eufy_clean_vacuum"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eufy Clean Vacuum."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                api = EufyClean(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                await api.init()

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )
            except Exception as err:
                _LOGGER.error("Failed to connect to Eufy Clean API: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
