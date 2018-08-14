#!/usr/bin/env python

import time, datetime
from influxdb import InfluxDBClient
import sensors


class LmSensorsMetrics(object):
  """
  Used for collecting metrics as discovered by PySensors(ln-sensors), such as 
  AMD-GPU (heat, fan RPM) and CPU Core-Temperature data.
  """
  __EPOC_SLEEP_SECONDS = 5
  __METRICS_DB = 'ethmetrics'
  _influxdb_client = InfluxDBClient('localhost', 8086, 'root', 'root', __METRICS_DB)

  def __init__(self):
    """
    Initilialize PySensors(lm-sensors) and InfluxDB clent
    """
    sensors.init()

  def start_collection(self):
    """
    Starts the data collection
    """
    print "Collecting AMD and CPU metrics...."
    while True:
      amdgpu_count = 0
      for chip in sensors.iter_detected_chips():
        if chip.prefix == 'amdgpu':
          self._collect_amd_gpu_metrics(chip, amdgpu_count)
          amdgpu_count += 1
        elif chip.prefix == 'coretemp':
          self._collect_cpu_metrics(chip)
      time.sleep(self.__EPOC_SLEEP_SECONDS)

  def _collect_amd_gpu_metrics(self, chip, amdgpu_count):
    """
    Collects AMD GPU metrics that are available via lm-sensors, such as heat and fan rpm.
    """  
    json_body = []
    for feature in chip:
      if feature.label.startswith('fan'):
        val = float(feature.get_value()) / 3200.0
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
    self._influxdb_client.write_points(json_body)

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
    self._influxdb_client.write_points(json_body)


if __name__ == "__main__":
  try:
    LmSensorsMetrics().start_collection()
  finally:
    sensors.cleanup()
