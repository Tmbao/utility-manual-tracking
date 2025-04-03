"""Interface for fitting data to a curve.
This is used for interpolation and extrapolation of data points.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime

GRANULAR_DELTA = datetime.timedelta(hours=1)


@dataclass(frozen=True)
class Datapoint:
    """Datapoint class."""

    value: float
    timestamp: datetime.datetime

    def as_dict(self) -> dict[str, float | str]:
        """Convert to dict."""
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @staticmethod
    def from_dict(data: dict[str, float | str]) -> Datapoint:
        """Convert from dict."""
        return Datapoint(
            value=data["value"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
        )


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
