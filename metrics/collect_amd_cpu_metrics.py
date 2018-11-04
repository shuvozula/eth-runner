#!/usr/bin/env python

from influxdb import InfluxDBClient
from log.log import LOG
from watchdog.lmsensors_watchdog import LmSensorsWatchdog

import datetime
import os
import sensors
import threading
import time


_EPOCH_SLEEP_SECONDS = 60
_PERIOD_SECONDS = 0.5
_METRICS_DB = 'ethmetrics'


class LmSensorsMetrics(threading.Thread):
  """
  Used for collecting metrics as discovered by PySensors(ln-sensors), such as
  AMD-GPU (heat, fan RPM) and CPU Core-Temperature data.
  """

  def __init__(self, host, port, exit_flag_event, thread_name):
    """
    Initilialize PySensors(lm-sensors) and InfluxDB clent
    """
    threading.Thread.__init__(self)
    self.name = thread_name

    LOG.info('Initializing Lm-sensors...')
    sensors.init()

    self._exit_flag_event = exit_flag_event
    self.influxdb_client = InfluxDBClient(host, port, 'root', 'root', _METRICS_DB)

    self._watchdog = LmSensorsWatchdog()

  def __del__(self):
    LOG.info('Shutting down AMD + CPU metrics collection....')
    sensors.cleanup()

  def run(self):
    """
    Starts the data collection
    """
    LOG.info('Collecting AMD and CPU metrics....')
    while not self._exit_flag_event.is_set():
      amdgpu_count = 0
      json_body = []
      for chip in sensors.iter_detected_chips():
        if chip.prefix == 'amdgpu':
          json_body.append(self._collect_amd_gpu_metrics(chip, amdgpu_count))
          amdgpu_count += 1
        elif chip.prefix == 'coretemp':
          json_body.append(self._collect_cpu_metrics(chip))

      self.influxdb_client.write_points(json_body)
      self._watchdog.do_monitor(json_body)
      time.sleep(_EPOCH_SLEEP_SECONDS)

    LOG.info('Exiting AMD GPU + CPU metrics collection....')

  def _collect_amd_gpu_metrics(self, chip, amdgpu_count):
    """
    Collects AMD GPU metrics that are available via lm-sensors, such as heat and fan rpm.
    """
    device_name = 'amd_%s' % amdgpu_count
    data = {
      'measurement': device_name,
      'tags': {
        'host': 'minar',
        'gpu': device_name
      },
      'fields': {}
    }
    for feature in chip:
      if feature.label.startswith('fan'):
        data['fields']['fan_speed'] = float(feature.get_value()) * 100.0 / 3200.0
      elif feature.label.startswith('temp'):
        data['fields']['temperature'] = feature.get_value()

    return data

  def _collect_cpu_metrics(self, chip):
    """
    Collects CPU heat from each core, as available from lm-sensors
    """
    data = {
      'measurement': 'cpu_temp',
      'tags': {
        'host': 'minar',
        'cpu': 'cpu'
      },
      'fields': {}
    }
    for feature in chip:
      if feature.label.startswith('Core'):
        data['fields']['core_temp_%s' % feature.label.replace(' ', '_')] = feature.get_value()

    return data
