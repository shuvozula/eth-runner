#!/usr/bin/env python

import threading
import time

from log.log import LOG

_EPOCH_SLEEP_SECONDS = 60
_WAKEUP_SLEEP_SECONDS = 10 * 60  # 10 mins


class AbstractMetricsCollector(threading.Thread):
  """
  Base class for metrics collection. Encapsulates the behavior of data-collection, reporting and
  monitoring (Command pattern)
  """

  def __init__(self, influxdb_client, watchdog, exit_flag_event):
    """
    """
    threading.Thread.__init__(self)

    if type(self) is AbstractMetricsCollector:
      raise NotImplementedError('Abstract class cannot be directly instantiated!')

    self.name = str(self)

    self._influxdb_client = influxdb_client
    self._watchdog = watchdog
    self._exit_flag_event = exit_flag_event

  def collect_metrics(self):
    raise NotImplementedError('Needs to be overriden by derived class.')

  def run(self):
    """
    Starts the data collection,
    """
    LOG.info('Collecting %s...', self)
    try:
      while not self._exit_flag_event.is_set():

        # call the derived methor for data, or a NotImplementedError is raised
        json_body = self.collect_metrics()

        # write metrics to InfluxDB
        self._influxdb_client.write_points(json_body)

        # monitor the data for any abnormalities in the AMD GPUs
        self._watchdog.do_monitor(json_body)

        time.sleep(_EPOCH_SLEEP_SECONDS)

      LOG.info('Exiting %s data collection...', self)

    except Exception:
      LOG.exception('Suffered a critical error while collecting metrics and monitoring!')
      self._watchdog.switch_off_miner(_WAKEUP_SLEEP_SECONDS)
