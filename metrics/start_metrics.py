#!/usr/bin/env python

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collect_amd_cpu_metrics import LmSensorsMetrics
from collect_nvidia_metrics import NvidiaMetrics

from log.log import LoggingInit
from log.log import LOG

import coloredlogs
import signal
import threading
import time


METRICS_HOST = '10.0.0.3'
METRICS_PORT = '8086'

LOG_PATH = '/var/log/'
LOG_FILE_NAME = 'metrics_runner'


class MetricsRunner(object):

  def __init__(self):
    signal.signal(signal.SIGINT, self._kill_callback)
    signal.signal(signal.SIGTERM, self._kill_callback)

    LoggingInit(LOG_PATH, LOG_FILE_NAME)
    coloredlogs.install()

  def __enter__(self):
    self.exit_flag_event = threading.Event()
    self.exit_flag_event.clear()
    self.lmsensors_metrics_thread = LmSensorsMetrics(name='AMD+GPU-Thread', 
      METRICS_HOST, METRICS_PORT, self.exit_flag_event)
    self.nvidia_gpu_metrics_thread = NvidiaMetrics(name='Nvidia-Thread',
      METRICS_HOST, METRICS_PORT, self.exit_flag_event)
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
