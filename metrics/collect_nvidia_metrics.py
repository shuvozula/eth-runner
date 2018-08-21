#!/usr/bin/env python

from influxdb import InfluxDBClient
from pynvml import (
  nvmlInit, 
  nvmlShutdown, 
  nvmlDeviceGetCount, 
  nvmlDeviceGetHandleByIndex,
  nvmlDeviceGetPowerUsage, 
  nvmlDeviceGetFanSpeed, 
  nvmlDeviceGetTemperature,
  NVML_TEMPERATURE_GPU,
)

import os
import time


class NvidiaMetrics(object):
  """
  Used for collecting NVIDIA GPU metrics, by tapping into the underlying NVML library
  available via pynvml. Power usage, Temperature and Fan-Speed are reported for each
  GPU to InfluxDB
  """
  _EPOCH_SLEEP_SECONDS = 5
  _METRICS_DB = 'ethmetrics'
  _influxdb_client = InfluxDBClient('localhost', 8086, 'root', 'root', _METRICS_DB)

  def __init__(self):
    """
    Initialize NVML and create a .pid file
    """
    nvmlInit()
    with open('/var/log/nvidia_metrics_collector.pid', 'w') as f:
      f.write(str(os.getpid()))

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """
    Cleans up the NVML internal state to all GPUs
    """
    nvmlShutdown()    

  def start_collection(self):
    """
    Start the NVIDIA GPU data collection
    """
    print "Collecting NVIDIA GPU metrics...."
    while True:
      json_body = []
      for gpu_num in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(gpu_num)
        device_name = 'nvidia.gpu.' + str(gpu_num)
        power_usage = float(nvmlDeviceGetPowerUsage(handle)) / 1000.0
        fan_speed = nvmlDeviceGetFanSpeed(handle)
        temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        data = {
          "measurement": device_name,
          "tags": {
            "host": "minar",
            "gpu": device_name
          },
          "fields": {
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "temperature": temperature
          }
        }
        json_body.append(data)
        time.sleep(0.5)
      self._influxdb_client.write_points(json_body)
      time.sleep(self._EPOCH_SLEEP_SECONDS)


if __name__ == "__main__":
  with NvidiaMetrics() as collector:
    collector.start_collection()
