#!/usr/bin/env python

# TODO:Remove this block later
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collect_amd_cpu_metrics import LmSensorsMetrics
from collect_nvidia_metrics import NvidiaMetrics
from influxdb import InfluxDBClient

from log.log import LoggingInit
from log.log import LOG

import signal
import threading
import time


METRICS_HOST = '10.0.0.3'
METRICS_PORT = '8086'
METRICS_USER = 'root'
METRICS_PASSWORD = 'root'
METRICS_DB = 'ethmetrics'

LOG_PATH = '/var/log/'
LOG_FILE_NAME = 'metrics_runner'
PID_FILE_LOCATION = '/var/log/metrics_collector.pid'


class MetricsRunner(object):

  def __init__(self):
    signal.signal(signal.SIGINT, self._kill_callback)
    signal.signal(signal.SIGTERM, self._kill_callback)

    LoggingInit(LOG_PATH, LOG_FILE_NAME)

    LOG.info('Creating pid file at %s with PID=[%s]...', PID_FILE_LOCATION, os.getpid())
    with open(PID_FILE_LOCATION, 'w') as f:
      f.write(str(os.getpid()))

  def __enter__(self):
    self.exit_flag_event = threading.Event()
    self.exit_flag_event.clear()
    self.influxdb_client = InfluxDBClient(METRICS_HOST, METRICS_PORT, METRICS_USER, METRICS_PASSWORD, METRICS_DB)
    self.lmsensors_metrics_thread = LmSensorsMetrics(
      influxdb_client=self.influxdb_client,
      exit_flag_event = self.exit_flag_event)
    self.nvidia_gpu_metrics_thread = NvidiaMetrics(
      influxdb_client=self.influxdb_client,
      exit_flag_event = self.exit_flag_event)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    pass

  def start_metrics_collection(self):
    self.lmsensors_metrics_thread.start()
    self.nvidia_gpu_metrics_thread.start()
    signal.pause()

  def _kill_callback(self, signum, frame):
    LOG.info('Stopping all metrics-collectors gracefully...')
    self.exit_flag_event.set()
    time.sleep(65)

    while self.lmsensors_metrics_thread.is_alive() and \
          self.nvidia_gpu_metrics_thread.is_alive():

      self.lmsensors_metrics_thread.join()
      LOG.info('Killed LmSensorsMetrics thread...')

      self.nvidia_gpu_metrics_thread.join()
      LOG.info('Killed NvidiaMetrics thread...')

    sys.exit(0)

if __name__ == '__main__':
    with MetricsRunner() as metrics_runner:
      metrics_runner.start_metrics_collection()
