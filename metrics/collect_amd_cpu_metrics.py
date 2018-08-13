#!/usr/bin/env python

from influxdb import InfluxDBClient
import sensors


class LmSensorsMetrics(object):
"""
Used for collecting metrics as discovered by PySensors(ln-sensors), such as 
AMD-GPU (heat, fan RPM) and CPU Core-Temperature data.
"""
  __METRICS_DB = 'ethmetrics'
  _influxdb_client

  def __init__(self):
    """
    Initilialize PySensors(lm-sensors) and InfluxDB clent
    """
    sensors.init()
    _influxdb_client = InfluxDBClient('localhost', 8086, 'root', 'root', __METRICS_DB)

  def start_collection(self):
    """
    Starts the data collection
    """
    print "Collecting AMD and CPU metrics...."
    while True:
      amdgpu_count = 0
      try:
        for chip in sensors.iter_detected_chips():
          if chip.prefix == 'amdgpu':
            self._collect_amd_gpu_metrics(chip, amdgpu_count)
            amdgpu_count += 1
          elif chip.prefix == 'coretemp':
            self._collect_cpu_metrics(chip)
      finally:
        sensors.cleanup()

  def _collect_amd_gpu_metrics(self, chip, amdgpu_count):
  """
  Collects AMD GPU metrics that are available via lm-sensors, such as heat and fan rpm.
  """  
    json_body = []
    for feature in chip:
      data = {
        "measurement": "amd_{%d}_{%s}".format(amdgpu_count, feature.label.replace(' ', '_')),
        "tags": {
          "host": "minar",
          "gpu": amdgpu_count
        },
        "time": "{:%Y-%m-%dT%H:%M:%S}Z".format(datetime.datetime.now())
        "fields": {
          "value": feature.get_value()
        }
      }
      json_body.append(data)
    _influxdb_client.write_points(json_body)

  def _collect_cpu_metrics(self, chip):
    """
    Collects CPU heat from each core, as available from lm-sensors
    """
    for feature in chip:
      if feature.label.startswith('Core'):
        data = {
          "measurement": "cpu_{%s}".format(feature.label.replace(' ', '_')),
          "tags": {
            "host": "minar",
            "cpu": amdgpu_count
          },
          "time": "{:%Y-%m-%dT%H:%M:%S}Z".format(datetime.datetime.now())
          "fields": {
            "value": feature.get_value()
          }
        }
        json_body.append(data)
    _influxdb_client.write_points(json_body)


if __name__ == "__main__":
  LmSensorsMetrics().start_collection()
