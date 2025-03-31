"""Interface for fitting data to a curve.
This is used for interpolation and extrapolation of data points.
"""

from __future__ import annotations

import datetime

GRANULAR_DELTA = datetime.timedelta(hours=1)


class Datapoint:
    def __init__(self, value: float, timestamp: datetime.datetime):
        self.value = value
        self.timestamp = timestamp


class Interpolate:
    def guesstimate(
        self, old_datapoints: list[Datapoint], new_datapoint: Datapoint
    ) -> Datapoint:
        """Guess the values between new and old datapoints."""
        pass


class Extrapolate:
    def guesstimate(
        self, datapoints: list[Datapoint], now: datetime.datetime
    ) -> Datapoint:
        """Guess the value of now based on datapoints."""
        pass
