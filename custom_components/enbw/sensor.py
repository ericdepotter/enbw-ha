"""Platform for sensor integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
import homeassistant.util.location as loc_util

from .const import (
    ATTR_AVAILABLE,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_TOTAL,
    CONF_ENBW_COORDINATOR,
    DOMAIN,
)
from .coordinator import (
    ENBWChargingPointCoordinatedEntity,
    ENBWChargingPointUpdateCoordinator,
)


@dataclass
class ENBWChargingPointSensorEntityDescription(SensorEntityDescription):
    """Describes ENBW ChargingPoint sensor entity."""

    attrs: Callable[[dict[str, Any]], dict[str, Any]] = lambda data: {}
    value_fn: Callable[[dict[str, Any]], StateType] | None = None


SENSOR_TYPES: tuple[ENBWChargingPointSensorEntityDescription, ...] = (
    ENBWChargingPointSensorEntityDescription(
        key="available_charging_points",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data[ATTR_AVAILABLE],
    ),
)

# ,
""" value_fn=lambda data: loc_util.distance(
    self.hass.config.latitude,
    self.hass.config.longitude,
    data["lat"],
    data["lon"],
)data[ battery_state_of_charge"] / 100 * data["autonomy"]"""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ENBW sensor entries."""
    enbw_coordinator = hass.data[DOMAIN][config_entry.entry_id][CONF_ENBW_COORDINATOR]
    async_add_entities(
        ENBWSensor(enbw_coordinator, description) for description in SENSOR_TYPES
    )


class ENBWSensor(
    ENBWChargingPointCoordinatedEntity,
    SensorEntity,
):
    """Representation of a ENBW Charging Point."""

    entity_description: ENBWChargingPointSensorEntityDescription

    _attr_latitude: float | None = None
    _attr_longitude: float | None = None
    _attr_distance_to_home: float | None = None
    _attr_total_number: float | None = None

    @property
    def latitude(self) -> float | None:
        """Return the latitude of this charging point."""
        return self._attr_latitude

    @property
    def longitude(self) -> float | None:
        """Return the longitude of this charging point."""
        return self._attr_longitude

    @property
    def distance_to_home(self) -> float | None:
        """Return the distance of this charging point to the configured home."""
        return self._attr_distance_to_home

    @property
    def total_points(self) -> float | None:
        """Return the total number of charging plugs of this charging point."""
        return self._attr_total_number

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the optional state attributes."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance_to_home": self.distance_to_home,
            "total_points": self.total_points,
        }

    def __init__(
        self,
        coordinator: ENBWChargingPointUpdateCoordinator,
        description: ENBWChargingPointSensorEntityDescription,
    ) -> None:
        """Initialize a ENBW Charging Point sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.entity_description.value_fn:
            self._attr_native_value = self.coordinator.data[self.entity_description.key]
        else:
            self._attr_native_value = self.entity_description.value_fn(
                self.coordinator.data
            )
        self._attr_extra_state_attributes = self.entity_description.attrs(
            self.coordinator.data
        )

        self._attr_latitude = self.coordinator.data.get(ATTR_LATITUDE)
        self._attr_longitude = self.coordinator.data.get(ATTR_LONGITUDE)
        self._attr_distance_to_home = loc_util.distance(
            self.hass.config.latitude,
            self.hass.config.longitude,
            self.coordinator.data[ATTR_LATITUDE],
            self.coordinator.data[ATTR_LONGITUDE],
        )
        self._attr_total_number = self.coordinator.data.get(ATTR_TOTAL)

        self.async_write_ha_state()
