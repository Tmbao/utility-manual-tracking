"""Sensor for Utility Manual Tracking"""

from __future__ import annotations

import asyncio

from datetime import datetime, timezone
import json
from homeassistant.components.sensor import SensorEntity, SensorStateClass
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
from custom_components.utility_manual_tracking.statistics import (
    backfill_statistics,
    reset_statistics,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = UtilityManualTrackingSensor(
        hass,
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
        self,
        hass: HomeAssistant,
        meter_name: str,
        meter_unit: str,
        meter_class: str,
        algorithm: str | None,
    ) -> None:
        super().__init__()
        self._attr_unique_id = (
            f"{DOMAIN}_{meter_name.lower().replace(' ', '_')}_{meter_class.lower()}"
        )
        self._attr_name = meter_name
        self._attr_device_class = meter_class
        self._attr_native_unit_of_measurement = meter_unit
        self._attr_state_class = SensorStateClass.TOTAL
        self.entity_id = f"sensor.{self._attr_unique_id}"

        self._algorithm: str = algorithm.lower() if algorithm else DEFAULT_ALGORITHM
        self._last_read_value: float = None
        self._last_updated: datetime | None = None
        self._previous_reads: list[dict[str, float | str]] = []

        self._load_attributes(hass)

    def set_value(self, value, date_utc) -> None:
        """Update the sensor state."""
        if self._last_read_value:
            if self._last_updated >= date_utc:
                raise ValueError(
                    f"New reading {date_utc} cannot be earlier than the last read {self._last_updated}"
                )

            self._previous_reads.append(
                Datapoint(self._last_read_value, self._last_updated).as_dict()
            )
            # Limit the number of previous reads to MAX_PREVIOUS_READS
            self._previous_reads = self._previous_reads[-self.MAX_PREVIOUS_READS :]

        self._last_read_value = value
        self._last_updated = date_utc

        missing_data = interpolate(
            self._algorithm,
            [Datapoint.from_dict(read) for read in self._previous_reads],
            Datapoint(self._last_read_value, self._last_updated),
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
                self._attr_native_unit_of_measurement,
                self._algorithm,
                missing_data + [Datapoint(self._last_read_value, self._last_updated)],
            ),
            self.hass.loop,
        ).result()
        LOGGER.debug(
            f"Backfilled statistics for {self.entity_id} with algorithm {self._algorithm}"
        )
        LOGGER.debug("Persisting attributes to storage")
        self._save_attributes()

    def reset_statistics(self) -> None:
        """Reset the statistics for the sensor."""
        if len(self._previous_reads) == 0:
            LOGGER.debug("No previous reads to reset")
            return

        LOGGER.debug(f"Resetting statistics for {self.entity_id}")
        reset_statistics(
            self.hass,
            self.unique_id,
            self._algorithm,
        )

        # Backfill statistics with the previous reads
        # and the last read value
        LOGGER.debug(
            f"Backfilling statistics for {self.entity_id} with algorithm {self._algorithm}"
        )
        reads_seen = []
        for read in self._previous_reads:
            if len(reads_seen) > 0:
                missing_data = interpolate(
                    self._algorithm,
                    [Datapoint.from_dict(read) for read in reads_seen],
                    Datapoint.from_dict(read),
                )

                asyncio.run_coroutine_threadsafe(
                    backfill_statistics(
                        self.hass,
                        self.unique_id,
                        self._attr_name,
                        self._attr_native_unit_of_measurement,
                        self._algorithm,
                        missing_data,
                    ),
                    self.hass.loop,
                ).result()
            reads_seen.append(read)

        if len(reads_seen) == 0:
            return

        missing_data = interpolate(
            self._algorithm,
            [Datapoint.from_dict(read) for read in reads_seen],
            Datapoint(self._last_read_value, self._last_updated),
        )
        asyncio.run_coroutine_threadsafe(
            backfill_statistics(
                self.hass,
                self.unique_id,
                self._attr_name,
                self._attr_native_unit_of_measurement,
                self._algorithm,
                missing_data + [Datapoint(self._last_read_value, self._last_updated)],
            ),
            self.hass.loop,
        ).result()

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return the state attributes."""
        return {
            "meter_name": self._attr_name,
            "last_updated": self._last_updated,
            "last_read": self._last_read_value,
            "previous_reads": json.dumps(self._previous_reads),
            "algorithm": self._algorithm,
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        latest_datapoint = extrapolate(
            self._algorithm,
            [Datapoint.from_dict(read) for read in self._previous_reads]
            + [Datapoint(self._last_read_value, self._last_updated)],
            datetime.now(timezone.utc),
        )
        if latest_datapoint:
            return latest_datapoint.value
        return None

    def _save_attributes(self) -> None:
        attributes = self.extra_state_attributes
        self.hass.data[DOMAIN][self.entity_id + "_attributes"] = attributes

    def _load_attributes(self, hass: HomeAssistant) -> None:
        attributes = hass.data[DOMAIN].get(self.entity_id + "_attributes")
        if attributes:
            LOGGER.debug("Loading attributes from storage")
            self._last_updated = attributes.get("last_updated")
            self._last_read_value = attributes.get("last_read")
            self._previous_reads = json.loads(attributes.get("previous_reads"))
            self._algorithm = attributes.get("algorithm")
