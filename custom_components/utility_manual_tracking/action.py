"""Actions for Utility Manual Tracking integration."""

from __future__ import annotations

from homeassistant.core import ServiceCall
from homeassistant.helpers import service

from custom_components.utility_manual_tracking.consts import DOMAIN, LOGGER
from custom_components.utility_manual_tracking.sensor import (
    UtilityManualTrackingSensor,
)


def handle_update_meter_value(call: ServiceCall):
    entities = service.async_extract_referenced_entity_ids(call.hass, call)
    value = call.data.get("value")
    for sensor_id in entities.referenced:
        sensor = call.hass.data.get(DOMAIN)[sensor_id[len("sensor.") :]]
        if isinstance(sensor, UtilityManualTrackingSensor):
            sensor.set_value(value)
            LOGGER.info(f"Updated sensor {sensor_id} with value {value}")
        else:
            LOGGER.error(
                f"Entity {sensor_id} is not a UtilityManualTrackingSensor, unable to update value."
            )
