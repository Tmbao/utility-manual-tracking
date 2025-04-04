# Utility manual tracking 

## Installation instructions
1. Make sure that you've had HACS installed (see [here](https://hacs.xyz/docs/user) for instructions).
2. Once HACS is installed, add the [](https://github.com/Tmbao/utility-manual-tracking.git) as a custom repository (Integration type), then you should be able to find this integration (**Utility manual tracking**) via HACS Integration and download it.
3. Once you've downloaded the integration, make sure to restart your Home Assistant Server. 
4. Come to **Devices & Services** in your Settings, hit **Add Integration** and find **Utility manual tracking**.
5. A config dialog should show up prompting you to setup a meter. Setting up the meter, ensure the meter unit adheres to HA Core `unit_of_measurement` (e.g. MJ, kWh) and the meter class adheres to HA Core `device_class` (e.g. energy, water).
6. Once the meter has been created, you can start recording the reading via the integration service call. Example below:
```yaml
action: utility_manual_tracking.update_meter_value
data:
  value: 11
target:
  # This is the id of the sensor you just created.
  entity_id: sensor.utility_manual_tracking_test_meter_kwh
```

For each device/meter added, the integration creates 2 statistics.
 - The meter sensor itself, where the state is extrapolated.
 - A statistics with data interpolated retrospectively.

## How this integration works
1. Each reading provided to the meter/sensor is treated as a datapoint. Associated to the timestamp in which the reading is added. Note that for this to work the reading has to be of `total_increasing`.
2. The statistics follows the datapoints that are provided, missing datapoints (e.g. missing hours) are interpolated with an algorithm. Note that due to limitation of statistics, the data cannot be more granular than hourly. If there are 2 readings taken in the same hour, the later one will take effect.
3. The sensor, on the other hand, tries to extrapolate the current reading using the same algorithm, and based on the same datapoints.

The number of datapoints kept is limited to 10 (soft limit).
The only algorithm implemented is linear interpolation/extrapolation (you can see `tests/test_linear_fitter.py` for details). 
