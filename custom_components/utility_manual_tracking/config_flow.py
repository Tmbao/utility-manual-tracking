"""Config flow for Utility Manual Tracking."""

from typing import Any
from custom_components.utility_manual_tracking.consts import (
    CONF_METER_NAME,
    CONF_METER_UNIT,
    DOMAIN,
)
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow


class UtilityManualTrackingConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_METER_NAME): str,
                        vol.Required(CONF_METER_UNIT): str,
                    }
                ),
                errors={},
            )

        return self.async_create_entry(
            title=user_input[CONF_METER_NAME],
            data={
                CONF_METER_NAME: user_input[CONF_METER_NAME],
                CONF_METER_UNIT: user_input[CONF_METER_UNIT],
            },
        )
