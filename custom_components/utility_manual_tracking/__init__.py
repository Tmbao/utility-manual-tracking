from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.utility_manual_tracking.action import handle_update_meter_value
from custom_components.utility_manual_tracking.consts import (
    DOMAIN,
    PLATFORMS,
)


def setup(hass: HomeAssistant, config: dict):
    """Setup the Utility Manual Tracking integration."""
    hass.data.setdefault(DOMAIN, {})
    hass.services.register(DOMAIN, "update_meter_value", handle_update_meter_value)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Utility Manual Tracking integration from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
