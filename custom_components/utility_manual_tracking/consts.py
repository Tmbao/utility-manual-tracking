"""Utility Manual Tracking Constants."""

import logging

from homeassistant.const import Platform

DOMAIN = "utility_manual_tracking"

CONF_METER_NAME = "meter_name"
CONF_METER_UNIT = "meter_unit"
CONF_METER_CLASS = "meter_class"

ATTRIBUTION = "Data provided by Amber Electric"

LOGGER = logging.getLogger(__package__)
PLATFORMS = [Platform.SENSOR]
