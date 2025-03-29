from homeassistant.core import ServiceCall
from homeassistant.helpers.entity import SensorEntity
from homeassistant.helpers import entity_registry

from custom_components.utility_manual_tracking.sensors import (
    UtilityManualTrackingSensor,
)


def handle_update_meter_value(call: ServiceCall):
    meter_id = call.data.get("meter_id")
    value = call.data.get("value")

    sensor = UtilityManualTrackingSensor(
        entity_registry.async_get_registry(call.hass).async_get(meter_id)
    )
    sensor.update(value)
