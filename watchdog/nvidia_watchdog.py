#!/usr/bin/env python

import time

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

PERIOD_SECS = 5  # seconds

MAX_HEATAGE_TOLERANCE = 5
MAX_POWER_TOLERANCE = 5


class NvidiaWatchdog(Watchdog):
  """
  Monitors the NVIDIA GPU's temperature and power-consumption.
  The moment the temperature goes above the specified threshold or
  the power drops below a certain threshold, stop the miners.
  """

  def __init__(self, exit_flag_event, timeout_seconds=120):
    super(NvidiaWatchdog, self).__init__(exit_flag_event, timeout_seconds)
    LOG.info("Nvidia-Watchdog started!")
    self.heatage_tolerance = 0
    self.power_tolerance = 0

  def do_monitor(self, data_list):
    for data in data_list:
      device_name = data['measurement']
      temperature = int(data['fields']['temperature'])
      power_usage = int(data['fields']['power_usage'])

      if temperature > HEAT_LIMIT:
        if self.heatage_tolerance > MAX_HEATAGE_TOLERANCE:
          LOG.error('Current temperature of Nvidia GPU-%s is %d > %d! Killing all miners...',
              device_name, temperature, HEAT_LIMIT)
          self.switch_off_miner_overheat(HEATAGE_SLEEP_TIMEOUT_MINS)
        else:
          self.heatage_tolerance += 1

      if power_usage < POWER_LIMIT:
        if self.power_tolerance > MAX_POWER_TOLERANCE:
          LOG.error('Current power usage from Nvidia GPU-%s is %d < %d! Killing all miners...',
              device_name, power_usage, POWER_LIMIT)
          self.switch_off_miner_underpowered(WATTAGE_SLEEP_TIMEOUT_MINS)
        else:
          self.power_tolerance += 1

      time.sleep(PERIOD_SECS)


