"""Actions for Utility Manual Tracking integration."""

from __future__ import annotations
from datetime import datetime, timezone

from homeassistant.core import ServiceCall
from homeassistant.helpers import service

from custom_components.utility_manual_tracking.consts import DOMAIN, LOGGER
from custom_components.utility_manual_tracking.sensor import (
    UtilityManualTrackingSensor,
)


DATE_FORMAT = "%Y-%m-%d %H"


def handle_update_meter_value(call: ServiceCall):
    entities = service.async_extract_referenced_entity_ids(call.hass, call)
    value = call.data.get("value")
    read_date_str = call.data.get("date")
    read_date_utc = (
        datetime.strptime(read_date_str, DATE_FORMAT).astimezone(timezone.utc)
        if read_date_str
        else datetime.now(timezone.utc)
    )
    for sensor_id in entities.referenced:
        sensor = call.hass.data.get(DOMAIN)[sensor_id]
        if isinstance(sensor, UtilityManualTrackingSensor):
            sensor.set_value(value, read_date_utc)
            LOGGER.info(f"Updated sensor {sensor_id} with value {value}")
        else:
            LOGGER.error(
                f"Entity {sensor_id} is not a UtilityManualTrackingSensor, unable to update value."
            )
