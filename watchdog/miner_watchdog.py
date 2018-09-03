#!/usr/bin/env python

from utils import delay_seconds
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
  NVMLError,
  NVMLError_GpuIsLost,
)

import logging
import os
import subprocess
import time

# Constants
__LOW_POWER_LIMIT_THRESHOLD = 55
__MAX_NVIDIA_HEATLIMIT = 75
__MAX_AMD_HEATLIMIT = 60
__START_DELAY = 120
__DELAY_BETWEEN_PINGS = 1
__WATTAGE_SLEEP_TIMEOUT = 5
__HEATAGE_SLEEP_TIMEOUT = 20

__MAX_ALERTS_COUNT = 5


class GpuLowPowerError(Exception):
  def __init__(self, message, errors):
    super().__init__('ERROR: !!GPU-Low-Power-Error!! ' + message)


class GpuHighHeatError(Exception):
  def __init__(self, message, errors):
    super().__init__('ERROR: !!GPU-High-Heat-Error!! ' + message)


class Watchdog(object):
  __NVIDIA_ETHMINER_PID_FILE_LOCATION = '/var/log/nvidia_miner.pid'
  __AMD_ETHMINER_PID_FILE_LOCATION = '/var/log/ati_miner.pid'

  _low_power_alerts_count = []
  _high_heat_alerts_count = []
  _nvidia_ethminer_pid = 0
  _amd_ethminer_pid = 0
  _collect_metrics = False
  _influxdb_client = InfluxDBClient('localhost', 8086, 'root', 'root', _METRICS_DB)

  def __init__(self, collect_metrics=False):
    """
    Initializes PyNVML and fetches the PIDs of the running Ethminer processes.
    """
    self._collect_metrics = collect_metrics
    if self._collect_metrics:
      self._json_body = []
    nvmlInit()
    getPids()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    nvmlShutdown()

  def getPids(self):
    """
    """
    with open(__NVIDIA_ETHMINER_PID_FILE_LOCATION) as f:
      self._nvidia_ethminer_pid = f.read().replace('\r\n', ' ')
    with open(__AMD_ETHMINER_PID_FILE_LOCATION) as f:
      self._amd_ethminer_pid = f.read().replace('\r\n', ' ')

  def check_wattage(self, gpu_name, power_usage):
    """
    """
    if power_usage < __LOW_POWER_LIMIT_THRESHOLD:
      print('GPU [' + + ']')
      _low_power_alerts_count += 1

    if _low_power_alerts_count > __MAX_ALERTS_COUNT:
      raise NvidiaGpuLowPowerError('GPU[' + gpu_name + '] triggered lower power alert!')

  def check_heatage(self, gpu_name, temperature):
    """
    """
    if temperature > __MAX_NVIDIA_HEATLIMIT or temperature > __MAX_AMD_HEATLIMIT:
      _high_heat_alerts_count += 1

    if _high_heat_alerts_count > __MAX_ALERTS_COUNT:
      raise NvidiaGpuHighHeatError('GPU[' + gpu_name + '] triggered a high heat alert!')

  def collect_metrics(self, device_name, data):
    """
    """
    if self._collect_metrics:
      self._json_body.append({
          "measurement": device_name,
          "tags": {
            "host": "minar",
            "gpu": device_name
          },
          "fields": {
            "power_usage": data.power_usage,
            "fan_speed": data.fan_speed,
            "temperature": data.temperature
          }  
        }
      )

  @delay_seconds(__DELAY_BETWEEN_PINGS)
  def write_metrics(self):
    """
    """
    if self._collect_metrics:
      self._influxdb_client.write_points(self._json_body)
      del self._json_body = [:]

  @delay_seconds(__DELAY_BETWEEN_PINGS)
  def fetch_metrics(self, handle, device_name):
    """
    """
    data = {
      device_name: device_name,
      power_usage: float(nvmlDeviceGetPowerUsage(handle)) / 1000.0,
      fan_speed: nvmlDeviceGetFanSpeed(handle),
      temperature: nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
    }
    return data

  def stop_miners(self, stack_trace):
    """
    """

  @delay_seconds(__START_DELAY)
  def start_watchdog(self):
    """
    Starts the watchdog after __START_DELAY seconds. Keeps looping infinitely until the process 
    gets killed or an error is raised by Alerts or a general driver error, in which case it kills
    the ethminer processes and begins to shutdown the system
    """
    print 'Watch-dog started!'

    while True:
      try:
        for gpu_num in range(nvmlDeviceGetCount()):
          handle = nvmlDeviceGetHandleByIndex(gpu_num)
          device_name = 'nvidia.gpu.' + str(gpu_num)
          
          data = fetch_metrics(handle, device_name)
          
          # monitor watts consumed and heat output to detect abnormalities
          check_wattage(gpu_name, data.power_usage)
          check_heatage(gpu_name, data.temperature)

          collect_metrics(device_name, data)
        write_metrics()

      except (NvidiaGpuLowPowerError, NvidiaGpuHighHeatError, NVMLError) as e:
        stop_miners(e)


# Traceback (most recent call last):
#   File "/home/shuvo/projects/eth-runner/metrics/collect_nvidia_metrics.py", line 79, in <module>
#     collector.start_collection()
#   File "/home/shuvo/projects/eth-runner/metrics/collect_nvidia_metrics.py", line 54, in start_collection
#     handle = nvmlDeviceGetHandleByIndex(gpu_num)
#   File "/usr/local/lib/python2.7/dist-packages/pynvml.py", line 807, in nvmlDeviceGetHandleByIndex
#     _nvmlCheckReturn(ret)
#   File "/usr/local/lib/python2.7/dist-packages/pynvml.py", line 310, in _nvmlCheckReturn
#     raise NVMLError(ret)
# pynvml.NVMLError_GpuIsLost: GPU is lost


if __name__ == '__main__':

  
  
  with NvidiaWatchdog() as watch_dog:
    print 'Starting NVIDIA watch-dog in ' + __START_DELAY + 'seconds...'
    watch_dog.start_watchdog()