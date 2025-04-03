"""Algorithms for utility manual tracking."""

from __future__ import annotations
import datetime

from dataclasses import dataclass

from custom_components.utility_manual_tracking.fitter import (
    Datapoint,
    Extrapolate,
    Interpolate,
)
from custom_components.utility_manual_tracking.linear_fitter import (
    LinearExtrapolate,
    LinearInterpolate,
)


@dataclass(frozen=True)
class Algorithm:
    """Algorithm class."""

    interpolate: Interpolate
    extrapolate: Extrapolate


ALGORITHMS: dict[str, Algorithm] = {
    "linear": Algorithm(LinearInterpolate(), LinearExtrapolate())
}

DEFAULT_ALGORITHM = "linear"


def interpolate(
    algorithm: str | None, old_datapoints: list[Datapoint], new_datapoint: Datapoint
) -> list[Datapoint]:
    """Interpolate a new datapoint based on old datapoints."""
    if algorithm is None or algorithm not in ALGORITHMS:
        algorithm = DEFAULT_ALGORITHM
    return ALGORITHMS[algorithm].interpolate.guesstimate(old_datapoints, new_datapoint)


def extrapolate(
    algorithm: str | None, datapoints: list[Datapoint], now: datetime.datetime
) -> Datapoint:
    """Extrapolate a new datapoint based on old datapoints."""
    if algorithm is None or algorithm not in ALGORITHMS:
        algorithm = DEFAULT_ALGORITHM
    return ALGORITHMS[algorithm].extrapolate.guesstimate(datapoints, now)
