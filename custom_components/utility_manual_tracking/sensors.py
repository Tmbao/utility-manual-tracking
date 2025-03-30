"""Sensor for Utility Manual Tracking"""

from __future__ import annotations

import datetime
from homeassistant.components.sensor import SensorEntity

from custom_components.utility_manual_tracking import UtilityManualTrackingConfigEntry


class UtilityManualTrackingSensor(SensorEntity):
    def __init__(self, meter_name: str, meter_unit: str, meter_class: str) -> None:
        super().__init__()
        self._meter_name = meter_name
        self._state: int = None
        self._last_updated = None
        self.device_class = meter_class
        self.unit_of_measurement = meter_unit

    def update(self, value) -> None:
        """Update the sensor state."""
        self._state = value
        self._last_updated = datetime.datetime.now()

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "meter_name": self._meter_name,
            "last_updated": self._last_updated,
        }

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._state
