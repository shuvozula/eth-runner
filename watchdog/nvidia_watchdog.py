#!/usr/bin/env python

from watchdog import Watchdog
from log.log import LOG


# Minimum power consumed by Nvidia device (Watts), below which something suspicious
# is happening and miners need to be rebooted
POWER_LIMIT = 55

# Maximum heat limit per Nvidia device allowed
HEAT_LIMIT = 78

# Minutes to sleep if either of the following (wattage, heat, etc.) send out alarms
HEATAGE_SLEEP_TIMEOUT_MINS = 20
WATTAGE_SLEEP_TIMEOUT_MINS = 5


class NvidiaWatchdog(Watchdog):
  """
  Monitors the NVIDIA GPU's temperature and power-consumption.
  The moment the temperature goes above the specified threshold or
  the power drops below a certain threshold, stop the miners.
  """

  def do_monitor(self, data_list):
    for data in data_list:
      device_name = data['measurement']
      temperature = int(data['fields']['temperature'])
      power_usage = int(data['fields']['power_usage'])

      if temperature > HEAT_LIMIT:
        LOG.error('Current temperature of Nvidia GPU-{} is {} > {}! Killing all miners...',
          device_name, temperature, HEAT_LIMIT)
        self.switch_off_miner(HEATAGE_SLEEP_TIMEOUT_MINS)

      if power_usage < POWER_LIMIT:
        LOG.error('Current power usage from Nvidia GPU-{} is {} < {}! Killing all miners...',
          device_name, power_usage, POWER_LIMIT)
        self.switch_off_miner(WATTAGE_SLEEP_TIMEOUT_MINS)

