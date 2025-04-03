from datetime import datetime
import json
from custom_components.utility_manual_tracking.fitter import Datapoint


def test_datapoint_serializable():
    """Test if Datapoint is serializable."""
    datapoint = Datapoint(1, datetime(2023, 10, 1, 0, 0))
    json_str = json.dumps(datapoint.as_dict())

    assert json_str == '{"value": 1, "timestamp": "2023-10-01T00:00:00"}'


def test_datapoint_deserializable():
    """Test if Datapoint is deserializable."""
    json_str = '{"value": 1, "timestamp": "2023-10-01T00:00:00"}'
    datapoint = Datapoint.from_dict(json.loads(json_str))

    assert datapoint.value == 1
    assert datapoint.timestamp == datetime(2023, 10, 1, 0, 0)
