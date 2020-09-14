#!/usr/bin/env python

from log.log import LOG
from metrics import AbstractMetricsCollector
from watchdog.lmsensors_watchdog import LmSensorsWatchdog

import sensors
import time


_PERIOD_SECONDS = 30


class LmSensorsMetrics(AbstractMetricsCollector):
  """
  Used for collecting metrics as discovered by PySensors(ln-sensors), such as
  AMD-GPU (heat, fan RPM) and CPU Core-Temperature data.
  """

  def __init__(self, influxdb_client, exit_flag_event):
    """
    Initialize PySensors(lm-sensors)
    """
    super(LmSensorsMetrics, self).__init__(
      influxdb_client=influxdb_client,
      watchdog=LmSensorsWatchdog(exit_flag_event),
      exit_flag_event=exit_flag_event
    )

    LOG.info('Initializing Lm-sensors...')
    sensors.init()

  def __str__(self):
    return 'LM-Sensors (AMD-Gpu + CPU) metrics'

  def __del__(self):
    LOG.info('Shutting down AMD + CPU metrics collection....')
    sensors.cleanup()

  def collect_metrics(self):
    """
    Starts the AMD GPU and CPU-core temperature data collection
    """
    amdgpu_count = 0
    json_body = []
    for chip in sensors.iter_detected_chips():
      if chip.prefix == b'amdgpu':
        json_body.append(self._collect_amd_gpu_metrics(chip, amdgpu_count))
        amdgpu_count += 1
      elif chip.prefix == b'coretemp':
        json_body.append(self._collect_cpu_metrics(chip))
      time.sleep(_PERIOD_SECONDS)

    return json_body

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
      elif feature.label.startswith('power'):
        data['fields']['power'] = feature.get_value()

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
