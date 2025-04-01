"""Implementation of a linear fitter for the utility manual tracking component."""

from __future__ import annotations
import datetime

from custom_components.utility_manual_tracking.fitter import (
    GRANULAR_DELTA,
    Datapoint,
    Extrapolate,
    Interpolate,
)


class LinearInterpolate(Interpolate):
    def guesstimate(
        self, old_datapoints: list[Datapoint], new_datapoint: Datapoint
    ) -> list[Datapoint]:
        # Implement linear interpolation logic here
        if len(old_datapoints) == 0:
            return []

        latest_old_datapoint = old_datapoints[-1]

        difference_time = (
            new_datapoint.timestamp - latest_old_datapoint.timestamp
        ).total_seconds() / GRANULAR_DELTA.total_seconds()
        difference = new_datapoint.value - latest_old_datapoint.value
        slope = difference / difference_time

        missing_datapoints: list[Datapoint] = []
        missing_timestamp = latest_old_datapoint.timestamp + GRANULAR_DELTA
        missing_value = latest_old_datapoint.value + slope
        while missing_timestamp < new_datapoint.timestamp:
            missing_datapoints.append(Datapoint(missing_value, missing_timestamp))
            missing_timestamp += GRANULAR_DELTA
            missing_value += slope
        return missing_datapoints


class LinearExtrapolate(Extrapolate):
    def guesstimate(
        self, datapoints: list[Datapoint], now: datetime.datetime
    ) -> Datapoint:
        # Implement linear extrapolation logic here

        if len(datapoints) == 0:
            return None

        if len(datapoints) == 1:
            return Datapoint(datapoints[0].value, now)

        latest_datapoint = datapoints[-1]
        second_latest_datapoint = datapoints[-2]
        difference_secs = (
            latest_datapoint.timestamp - second_latest_datapoint.timestamp
        ).total_seconds()
        difference = latest_datapoint.value - second_latest_datapoint.value
        slope = difference / difference_secs

        return Datapoint(
            latest_datapoint.value
            + slope * (now - latest_datapoint.timestamp).total_seconds(),
            now,
        )
