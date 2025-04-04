from homeassistant.components.recorder.models import StatisticMetaData, StatisticData
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.core import HomeAssistant

from custom_components.utility_manual_tracking.consts import DOMAIN, LOGGER
from custom_components.utility_manual_tracking.fitter import Datapoint


async def backfill_statistics(
    hass: HomeAssistant,
    sensor_id: str,
    meter_name: str,
    meter_unit: str,
    algorithm: str,
    datapoints: list[Datapoint],
) -> None:

    statistics_id: str = f"{DOMAIN}:{sensor_id}_statistics_{algorithm}"
    metadata = StatisticMetaData(
        has_mean=False,
        has_sum=True,
        name=f"{meter_name} - statistics ({algorithm})",
        source=DOMAIN,
        statistic_id=statistics_id,
        unit_of_measurement=meter_unit,
    )

    statistics: list[StatisticData] = []
    for datapoint in datapoints:
        start_timestamp = datapoint.timestamp.replace(minute=0, second=0, microsecond=0)
        statistics.append(
            StatisticData(
                sum=datapoint.value,
                start=start_timestamp,
            )
        )

    LOGGER.debug(f"Writing statistics {statistics_id}: {len(statistics)} datapoints")
    async_add_external_statistics(hass, metadata, statistics)
