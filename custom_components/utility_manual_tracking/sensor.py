"""Sensor for Utility Manual Tracking"""

from __future__ import annotations

import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.utility_manual_tracking.consts import (
    CONF_METER_CLASS,
    CONF_METER_NAME,
    CONF_METER_UNIT,
    DOMAIN,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = UtilityManualTrackingSensor(
        entry.data[CONF_METER_NAME],
        entry.data[CONF_METER_UNIT],
        entry.data[CONF_METER_CLASS],
    )
    hass.data.get(DOMAIN)[sensor.unique_id] = sensor

    async_add_entities([sensor])


class UtilityManualTrackingSensor(SensorEntity):
    def __init__(self, meter_name: str, meter_unit: str, meter_class: str) -> None:
        super().__init__()
        self._attr_unique_id = (
            f"{DOMAIN}_{meter_name.lower().replace(' ', '_')}_{meter_unit.lower()}"
        )
        self._attr_name = meter_name
        self._state: int = None
        self._last_updated = None
        self._attr_device_class = meter_class
        self._attr_unit_of_measurement = meter_unit

    def set_value(self, value) -> None:
        """Update the sensor state."""
        self._state = value
        self._last_updated = datetime.datetime.now()

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "meter_name": self._attr_name,
            "last_updated": self._last_updated,
        }

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._state
