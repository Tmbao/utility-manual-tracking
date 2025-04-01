"""Interface for fitting data to a curve.
This is used for interpolation and extrapolation of data points.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import datetime

from attr import dataclass

GRANULAR_DELTA = datetime.timedelta(hours=1)


@dataclass
class Datapoint:
    """Datapoint class."""
    value: float
    timestamp: datetime.datetime


class Interpolate(ABC):
    @abstractmethod
    def guesstimate(
        self, old_datapoints: list[Datapoint], new_datapoint: Datapoint
    ) -> Datapoint:
        """Guess the values between new and old datapoints."""
        pass


class Extrapolate(ABC):
    @abstractmethod
    def guesstimate(
        self, datapoints: list[Datapoint], now: datetime.datetime
    ) -> Datapoint:
        """Guess the value of now based on datapoints."""
        pass
