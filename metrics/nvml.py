#!/usr/bin/env python

import time

from pynvml import (
    NVML_TEMPERATURE_GPU,
    nvmlDeviceGetCount,
    nvmlDeviceGetFanSpeed,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetPowerUsage,
    nvmlDeviceGetTemperature,
)

from metrics import AbstractMetricsCollector
from watchdog.nvidia import Nvidia


DEVICE_NAME_FORMAT = 'nvidia.gpu.%d'
PERIOD_SECS = 0.5


class NvidiaMetrics(AbstractMetricsCollector):
    """
    Used for collecting NVIDIA GPU metrics, by tapping into the underlying NVML library
    available via pynvml. Power usage, Temperature and Fan-Speed are reported for each
    GPU to InfluxDB
    """

    def __init__(self, influxdb_client, exit_flag_event):
        """
        Initialize NVML
        """
        super(NvidiaMetrics, self).__init__(
            influxdb_client=influxdb_client,
            watchdog=Nvidia(exit_flag_event),
            exit_flag_event=exit_flag_event
        )

    def __str__(self):
        return 'NVIDIA GPU metrics'

    def collect_metrics(self):
        """
        Collect NVIDIA GPU metrics (eg: Temperature, Power-Consumption, fan-speed, etc.)
        """
        data_list = []
        for gpu_num in range(nvmlDeviceGetCount()):
            handle = nvmlDeviceGetHandleByIndex(gpu_num)
            device_name = DEVICE_NAME_FORMAT % gpu_num
            power_usage = float(nvmlDeviceGetPowerUsage(handle)) / 1000.0
            fan_speed = nvmlDeviceGetFanSpeed(handle)
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            data_list.append({
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
            })
            time.sleep(PERIOD_SECS)

        return data_list
