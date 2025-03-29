from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.utility_manual_tracking.actions import handle_update_meter_value
from custom_components.utility_manual_tracking.consts import (
    CONF_METER_CLASS,
    CONF_METER_NAME,
    CONF_METER_UNIT,
    DOMAIN,
    PLATFORMS,
)
from custom_components.utility_manual_tracking.sensors import (
    UtilityManualTrackingSensor,
)

type UtilityManualTrackingConfigEntry = ConfigEntry[UtilityManualTrackingSensor]


async def async_setup_entry(
    hass: HomeAssistant, entry: UtilityManualTrackingConfigEntry
) -> bool:
    """Set up the Utility Manual Tracking integration from a config entry."""

    sensor = UtilityManualTrackingSensor(
        entry.data[CONF_METER_NAME], entry.data[CONF_METER_UNIT], entry.data[CONF_METER_CLASS]
    )
    entry.runtime_data = [sensor]
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.services.register(DOMAIN, "update_meter_value", handle_update_meter_value)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: UtilityManualTrackingConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
