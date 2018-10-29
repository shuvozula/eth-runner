#!/usr/bin/env python

from influxdb import InfluxDBClient
from log.log import LOG, file_logging_handler
from log.filters import ThreadLoggingFilter

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
import threading
import time


_DEVICE_NAME_FORMAT = 'nvidia.gpu.%d'
_EPOCH_SLEEP_SECONDS = 60
_PERIOD_SECS = 0.5
_METRICS_DB = 'ethmetrics'
_PID_FILE_LOCATION = '/var/log/nvidia_metrics_collector.pid'


class NvidiaMetrics(threading.Thread):
  """
  Used for collecting NVIDIA GPU metrics, by tapping into the underlying NVML library
  available via pynvml. Power usage, Temperature and Fan-Speed are reported for each
  GPU to InfluxDB
  """
  def __init__(self, metrics_host, metrics_port, exit_flag_event):
    """
    Initialize NVML and create a .pid file
    """
    threading.Thread.__init__(self)
    file_logging_handler.addFilter(ThreadLoggingFilter(self))

    LOG.info('Initializing NVML sensors....')
    nvmlInit()

    LOG.info('Creating pid file at %s with PID=[%s]...', _PID_FILE_LOCATION, os.getpid())
    with open(_PID_FILE_LOCATION, 'w') as f:
      f.write(str(os.getpid()))

    self._exit_flag_event = exit_flag_event
    self.influxdb_client = InfluxDBClient(metrics_host, metrics_port, 
      'root', 'root', _METRICS_DB)
    
  def __del__(self):
    """
    Cleans up the NVML internal state for all GPUs
    """
    LOG.info("Shutting down NVIDA metrics collection....")
    nvmlShutdown()

  def run(self):
    """
    Start the NVIDIA GPU data collection
    """
    LOG.info('Collecting NVIDIA GPU metrics....')
    while not self._exit_flag_event.is_set():
      json_body = []
      for gpu_num in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(gpu_num)
        device_name = _DEVICE_NAME_FORMAT % gpu_num
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
        time.sleep(_PERIOD_SECS)
      self.influxdb_client.write_points(json_body)
      time.sleep(_EPOCH_SLEEP_SECONDS)
    LOG.info("Exiting Nvidia GPU metrics collection....")
