#!/usr/bin/env python

from influxdb import InfluxDBClient
from log.log import LOG
from watchdog.nvidia_watchdog import NvidiaWatchdog, HEATAGE_SLEEP_TIMEOUT_MINS
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


DEVICE_NAME_FORMAT = 'nvidia.gpu.%d'
EPOCH_SLEEP_SECONDS = 60
PERIOD_SECS = 0.5
METRICS_DB = 'ethmetrics'


class NvidiaMetrics(threading.Thread):
  """
  Used for collecting NVIDIA GPU metrics, by tapping into the underlying NVML library
  available via pynvml. Power usage, Temperature and Fan-Speed are reported for each
  GPU to InfluxDB
  """

  def __init__(self, host, port, exit_flag_event, thread_name):
    """
    Initialize NVML and create a .pid file
    """
    threading.Thread.__init__(self)
    self.name = thread_name

    LOG.info('Initializing NVML sensors....')
    nvmlInit()

    self._exit_flag_event = exit_flag_event
    self._influxdb_client = InfluxDBClient(host, port, 'root', 'root', METRICS_DB)

    self._watchdog = NvidiaWatchdog()

  def __del__(self):
    """
    Cleans up the NVML internal state for all GPUs
    """
    LOG.info('Shutting down NVIDA metrics collection....')
    nvmlShutdown()

  def run(self):
    """
    Start the NVIDIA GPU data collection
    """
    LOG.info('Collecting NVIDIA GPU metrics....')
    try:
      while not self._exit_flag_event.is_set():
        data_list = []
        for gpu_num in range(nvmlDeviceGetCount()):
          handle = nvmlDeviceGetHandleByIndex(gpu_num)
          device_name = DEVICE_NAME_FORMAT % gpu_num
          power_usage = float(nvmlDeviceGetPowerUsage(handle)) / 1000.0
          fan_speed = nvmlDeviceGetFanSpeed(handle)
          temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
          data = {
            'measurement': device_name,
            'tags': {
              'host': 'minar',
              'gpu': device_name
            },
            'fields': {
              'power_usage': power_usage,
              'fan_speed': fan_speed,
              'temperature': temperature
            }
          }
          data_list.append(data)
          time.sleep(PERIOD_SECS)

        # Write metrics to InfluxDB
        self._influxdb_client.write_points(data_list)

        # Monitor the data for any abnormalities and accordingly take precationary measures
        self._watchdog.do_monitor(data_list)

        time.sleep(EPOCH_SLEEP_SECONDS)

      LOG.info('Exiting Nvidia GPU metrics collection....')

    except Exception as e:
      LOG.error('Suffered a critical error: {}', e)
      self._watchdog.stop_miner(HEATAGE_SLEEP_TIMEOUT_MINS * 60)

