"""Actions for Utility Manual Tracking integration."""

from __future__ import annotations

from homeassistant.core import ServiceCall
from homeassistant.helpers import entity_registry, service

from custom_components.utility_manual_tracking.sensor import (
    UtilityManualTrackingSensor,
)


def handle_update_meter_value(call: ServiceCall):
    entities = service.async_extract_referenced_entity_ids(call.hass, call)
    value = call.data.get("value")
    for sensor_id in entities.referenced:
        sensor = entity_registry.async_get(call.hass).async_get(sensor_id)
        if isinstance(sensor, UtilityManualTrackingSensor):
            sensor.set_value(value)
