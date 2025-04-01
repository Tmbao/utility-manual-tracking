from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.core import HomeAssistant

from custom_components.utility_manual_tracking.consts import DOMAIN
from custom_components.utility_manual_tracking.fitter import Datapoint


async def backfill_statistics(
    hass: HomeAssistant,
    sensor_id: str,
    meter_name: str,
    meter_unit: str,
    algorithm: str,
    datapoints: list[Datapoint],
) -> None:

    metadata = StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f"{meter_name} - statistics ({algorithm})",
        source=DOMAIN,
        statistic_id=f"{sensor_id}_statistics_{algorithm}",
        unit_of_measurement=meter_unit,
    )

    statistics: list[StatisticData] = []
    for datapoint in datapoints:
        statistics.append(
            StatisticData(
                sum=datapoint.value,
                start=datapoint.timestamp,
            )
        )

    async_add_external_statistics(hass, metadata, statistics)
