"""Sensor for Utility Manual Tracking"""

from __future__ import annotations

import asyncio

from datetime import datetime, timezone
import json
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.utility_manual_tracking.algorithms import (
    DEFAULT_ALGORITHM,
    extrapolate,
    interpolate,
)
from custom_components.utility_manual_tracking.consts import (
    CONF_ALGORITHM,
    CONF_METER_CLASS,
    CONF_METER_NAME,
    CONF_METER_UNIT,
    DOMAIN,
    LOGGER,
)
from custom_components.utility_manual_tracking.fitter import Datapoint
from custom_components.utility_manual_tracking.statistics import backfill_statistics


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = UtilityManualTrackingSensor(
        entry.data[CONF_METER_NAME],
        entry.data[CONF_METER_UNIT],
        entry.data[CONF_METER_CLASS],
        entry.data[CONF_ALGORITHM],
    )
    hass.data.get(DOMAIN)[sensor.entity_id] = sensor
    LOGGER.info(
        f"Setting up Utility Manual Tracking sensor: {sensor.entity_id} with name {sensor.name}"
    )

    async_add_entities([sensor])


class UtilityManualTrackingSensor(SensorEntity):
    MAX_PREVIOUS_READS = 10

    def __init__(
        self, meter_name: str, meter_unit: str, meter_class: str, algorithm: str | None
    ) -> None:
        super().__init__()
        self._attr_unique_id = (
            f"{DOMAIN}_{meter_name.lower().replace(' ', '_')}_{meter_unit.lower()}"
        )
        self._attr_name = meter_name
        self._state: float = None
        self._attr_device_class = meter_class
        self._attr_unit_of_measurement = meter_unit
        self.entity_id = f"sensor.{self._attr_unique_id}"

        self._algorithm: str = algorithm.lower() if algorithm else DEFAULT_ALGORITHM
        self._last_read: float = None
        self._last_updated: datetime | None = None
        self._previous_reads: list[dict[str, float | str]] = []

    def set_value(self, value) -> None:
        """Update the sensor state."""
        if self._last_read is not None:
            self._previous_reads.append(
                Datapoint(self._last_read, self._last_updated).as_dict()
            )
            # Limit the number of previous reads to MAX_PREVIOUS_READS
            self._previous_reads = self._previous_reads[-self.MAX_PREVIOUS_READS :]

        self._state = value
        self._last_read = value
        self._last_updated = datetime.now(timezone.utc)

        missing_data = interpolate(
            self._algorithm,
            [Datapoint.from_dict(read) for read in self._previous_reads],
            Datapoint(self._state, self._last_updated),
        )

        LOGGER.debug(
            f"Interpolating missing data with algorithm {self._algorithm}: {missing_data}"
        )

        LOGGER.debug(
            f"Backfilling statistics for {self.entity_id} with algorithm {self._algorithm}"
        )
        asyncio.run_coroutine_threadsafe(
            backfill_statistics(
                self.hass,
                self.unique_id,
                self._attr_name,
                self._attr_unit_of_measurement,
                self._algorithm,
                missing_data + [Datapoint(self._state, self._last_updated)],
            ),
            self.hass.loop,
        ).result()
        LOGGER.debug(
            f"Backfilled statistics for {self.entity_id} with algorithm {self._algorithm}"
        )

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "meter_name": self._attr_name,
            "last_updated": self._last_updated,
            "previous_reads": json.dumps(self._previous_reads),
            "algorithm": self._algorithm,
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        latest_datapoint = extrapolate(
            self._algorithm,
            [Datapoint.from_dict(read) for read in self._previous_reads],
            datetime.now(timezone.utc),
        )
        if latest_datapoint is not None:
            return latest_datapoint.value
        return None
