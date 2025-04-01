from datetime import datetime

from custom_components.utility_manual_tracking.algorithms import (
    extrapolate,
    interpolate,
)
from custom_components.utility_manual_tracking.fitter import Datapoint


def test_linear_interpolate_normal():
    """Test linear interpolation."""

    old_datapoints = [
        Datapoint(1, datetime(2023, 10, 1, 0, 0)),
        Datapoint(2, datetime(2023, 10, 1, 1, 0)),
    ]
    new_datapoint = Datapoint(5, datetime(2023, 10, 1, 4, 0))

    missing_datapoints = interpolate("linear", old_datapoints, new_datapoint)

    assert len(missing_datapoints) == 2
    assert missing_datapoints[0].value == 3
    assert missing_datapoints[0].timestamp == datetime(2023, 10, 1, 2, 0)
    assert missing_datapoints[1].value == 4
    assert missing_datapoints[1].timestamp == datetime(2023, 10, 1, 3, 0)


def test_linear_interpolate_no_old_datapoints():
    """Test linear interpolation with no old datapoints."""

    old_datapoints = []
    new_datapoint = Datapoint(5, datetime(2023, 10, 1, 4, 0))

    missing_datapoints = interpolate("linear", old_datapoints, new_datapoint)

    assert len(missing_datapoints) == 0


def test_linear_extrapolate_normal():
    """Test linear extrapolation."""

    datapoints = [
        Datapoint(1, datetime(2023, 10, 1, 0, 0)),
        Datapoint(2, datetime(2023, 10, 1, 1, 0)),
    ]
    now = datetime(2023, 10, 1, 4, 0)

    extrapolated_datapoint = extrapolate("linear", datapoints, now)

    assert extrapolated_datapoint.value == 5
    assert extrapolated_datapoint.timestamp == now


def test_linear_extrapolate_no_datapoints():
    """Test linear extrapolation with no datapoints."""
    datapoints = []
    now = datetime(2023, 10, 1, 4, 0)

    extrapolated_datapoint = extrapolate("linear", datapoints, now)

    assert extrapolated_datapoint is None


def test_linear_extrapolate_one_datapoint():
    """Test linear extrapolation with one datapoint."""
    datapoints = [
        Datapoint(1, datetime(2023, 10, 1, 0, 0)),
    ]
    now = datetime(2023, 10, 1, 4, 0)

    extrapolated_datapoint = extrapolate("linear", datapoints, now)

    assert extrapolated_datapoint.value == 1
    assert extrapolated_datapoint.timestamp == now