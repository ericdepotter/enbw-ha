"""Config flow for ENBW integration."""

from __future__ import annotations

import logging
from typing import Any

from requests import HTTPError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ID, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from ._client import ENBWAPIClient
from .const import CONF_AUTH, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): str,
        vol.Optional(CONF_API_KEY): str,
    }
)


class ENBWHub:
    """ENBW Hub that authenticates with the API."""

    enbw_api = None

    def __init__(self) -> None:
        """Initialize."""
        self.auth = None

    def authenticate(self, id: str, api_key: str) -> bool:
        """Test if we can authenticate with the host."""
        try:
            self.enbw_api = ENBWAPIClient()
            self.enbw_api.login(id, api_key)
        except HTTPError as http_err:
            if http_err.response.status_code == 401:
                raise InvalidAuth
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise CannotConnect
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = ENBWHub()

    result = await hass.async_add_executor_job(
        hub.authenticate, data[CONF_ID], data[CONF_API_KEY]
    )
    if not result:
        raise InvalidAuth

    return {
        f"{CONF_AUTH}": hub.auth,
        f"{CONF_ID}": data[CONF_ID],
        f"{CONF_API_KEY}": data[CONF_API_KEY],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ENBW."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info[CONF_ID])
                return self.async_create_entry(title=info[CONF_ID], data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
