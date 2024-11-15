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

from .const import CONF_ENBW_COORDINATOR, DOMAIN
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
        key="lat",
        translation_key="latitude",
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ENBWChargingPointSensorEntityDescription(
        key="lon",
        translation_key="longitude",
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ENBWChargingPointSensorEntityDescription(
        key="distance_to_home",
        translation_key="distance_to_home",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data, hass: loc_util.distance(
            hass.config.latitude,
            hass.config.longitude,
            data["lat"],
            data["lon"],
        ),
    ),
    ENBWChargingPointSensorEntityDescription(
        key="numberOfChargePoints",
        translation_key="total_charging_points",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ENBWChargingPointSensorEntityDescription(
        key="availableChargePoints",
        translation_key="available_charging_points",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ENBWChargingPointSensorEntityDescription(
        key="state",
        translation_key="state",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: "available"
        if data["availableChargePoints"] > 0
        else "unavailable",
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


class ENBWSensor(ENBWChargingPointCoordinatedEntity, SensorEntity):
    """Representation of a ENBW Charging Point."""

    entity_description: ENBWChargingPointSensorEntityDescription

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
                self.coordinator.data, self.hass
            )
        self._attr_extra_state_attributes = self.entity_description.attrs(
            self.coordinator.data
        )
        self.async_write_ha_state()
