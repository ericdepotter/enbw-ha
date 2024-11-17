"""The ENBW integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_ID, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from ._client import ENBWAPIClient
from .const import (
    CONF_API,
    CONF_ENBW_COORDINATOR,
    DOMAIN,
)
from .coordinator import ENBWChargingPointUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ENBW from a config entry."""
    enbw_api = ENBWAPIClient()
    await hass.async_add_executor_job(
        enbw_api.login, entry.data[CONF_ID], entry.data[CONF_API_KEY]
    )

    # all coordinators shall share the same device
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=enbw_api.operator,
        model=enbw_api.model,
    )

    enbw_coordinator = ENBWChargingPointUpdateCoordinator(hass, device, enbw_api)

    await enbw_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_API: enbw_api,
        CONF_ENBW_COORDINATOR: enbw_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:  # noqa: SIM105
        # logging out any of them suffices; we don't care which one
        await hass.async_add_executor_job(
            hass.data[DOMAIN][entry.entry_id][CONF_ENBW_COORDINATOR].logout
        )
    except:  # noqa: E722
        # ignore any errors
        pass
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
