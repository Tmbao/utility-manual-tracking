from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from custom_components.utility_manual_tracking import UtilityManualTrackingConfigEntry


class UtilityManualTrackingSensor(SensorEntity):
    def __init__(self, meter_name: str, meter_unit: str) -> None:
        super().__init__()
        self._meter_name = meter_name
        self.unit_of_measurement = meter_unit
        self._state: int = None

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._state
