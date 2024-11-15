"""Define a custom data update coordinator for ENBW."""

import asyncio
from datetime import timedelta
import logging

from requests import HTTPError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from ._client import ENBWAPIClient
from .const import ATTR_MANUFACTURER, ATTR_MODEL, ATTRIBUTION, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ENBWChargingPointUpdateCoordinator(DataUpdateCoordinator):
    """ENBW coordinator to fetch data from the inofficial API at a set interval."""

    config_entry: ConfigEntry
    device_info: DeviceInfo

    def __init__(
        self,
        hass: HomeAssistant,
        device: DeviceInfo,
        enbw_api: ENBWAPIClient,
        update_interval=timedelta(minutes=1),
    ) -> None:
        """Initialize the coordinator with the given API client."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)
        _LOGGER.info("Initializing ENBWCoordinator")
        self.enbw_api = enbw_api
        self.device_info = device

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(30):
                enbw = await self.hass.async_add_executor_job(
                    self.enbw_api.get_charging_point_info
                )
                # can change over time, so we need to update it
                self.device_info["manufacturer"] = enbw.get(ATTR_MANUFACTURER)
                self.device_info["model"] = enbw.get(ATTR_MODEL)
                _LOGGER.debug("ENBW data fetched: %s", enbw)
                return enbw
        except HTTPError as http_err:
            if http_err.response.status_code == 401:
                raise UpdateFailed("Unable to fetch data from ENBW API") from http_err
            raise UpdateFailed(
                f"Error communicating with API: {http_err}"
            ) from http_err


class ENBWChargingPointCoordinatedEntity(
    CoordinatorEntity[ENBWChargingPointUpdateCoordinator]
):
    """Defines a base ENBW entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: ENBWChargingPointUpdateCoordinator,
    ) -> None:
        """Initialize the coordinated ENBW Device."""
        CoordinatorEntity.__init__(self, coordinator=coordinator)
        self._attr_device_info = coordinator.device_info
