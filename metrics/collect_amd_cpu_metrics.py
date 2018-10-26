#!/usr/bin/env python

from influxdb import InfluxDBClient

import datetime
import logging
import os
import sensors
import threading
import time


_EPOCH_SLEEP_SECONDS = 60
_PERIOD_SECONDS = 0.5
_METRICS_DB = 'ethmetrics'
_PID_FILE_LOCATION = '/var/log/amd_cpu_metrics_collector.pid'


logger = logging.getLogger()


class LmSensorsMetrics(threading.Thread):
  """
  Used for collecting metrics as discovered by PySensors(ln-sensors), such as 
  AMD-GPU (heat, fan RPM) and CPU Core-Temperature data.
  """
  def __init__(self, metrics_host, metrics_port, exit_flag_event):
    """
    Initilialize PySensors(lm-sensors) and InfluxDB clent
    """
    threading.Thread.__init__(self)

    logger.info('initializing Lm-sensors...')
    sensors.init()

    logger.info('creating pid file at %s with PID=[%s]...', _PID_FILE_LOCATION, os.getpid())
    with open(_PID_FILE_LOCATION, 'w') as f:
      f.write(str(os.getpid()))

    self._exit_flag_event = exit_flag_event
    self.influxdb_client = InfluxDBClient(metrics_host, metrics_port, 
      'root', 'root', _METRICS_DB)
    
  def __del__(self):
    sensors.cleanup()

  def run(self):
    """
    Starts the data collection
    """
    logger.info("Collecting AMD and CPU metrics....")
    while not self._exit_flag_event.is_set():
      amdgpu_count = 0
      for chip in sensors.iter_detected_chips():
        if chip.prefix == 'amdgpu':
          self._collect_amd_gpu_metrics(chip, amdgpu_count)
          amdgpu_count += 1
        elif chip.prefix == 'coretemp':
          self._collect_cpu_metrics(chip)
      time.sleep(_EPOCH_SLEEP_SECONDS)
    logger.info("Exiting AMD GPU + CPU metrics collection....")

  def _collect_amd_gpu_metrics(self, chip, amdgpu_count):
    """
    Collects AMD GPU metrics that are available via lm-sensors, such as heat and fan rpm.
    """  
    json_body = []
    for feature in chip:
      if feature.label.startswith('fan'):
        val = float(feature.get_value()) * 100.0 / 3200.0
      else:
        val = feature.get_value()
      data = {
        "measurement": "amd_%s_%s" % (amdgpu_count, feature.label.replace(' ', '_')),
        "tags": {
          "host": "minar",
          "gpu": amdgpu_count
        },
        "fields": {
          "gpu": val
        }
      }
      json_body.append(data)
      time.sleep(_PERIOD_SECONDS)
    self.influxdb_client.write_points(json_body)

  def _collect_cpu_metrics(self, chip):
    """
    Collects CPU heat from each core, as available from lm-sensors
    """
    json_body = []
    for feature in chip:
      if feature.label.startswith('Core'):
        data = {
          "measurement": "cpu_%s" % (feature.label.replace(' ', '_')),
          "tags": {
            "host": "minar",
            "cpu": feature.label.replace(' ', '_')
          },
          "fields": {
            "cpu": feature.get_value()
          }
        }
        json_body.append(data)
        time.sleep(_PERIOD_SECONDS)
    self.influxdb_client.write_points(json_body)
