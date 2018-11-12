#!/usr/bin/env python

# TODO:Remove this block later
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collect_amd_cpu_metrics import LmSensorsMetrics
from collect_nvidia_metrics import NvidiaMetrics
from influxdb import InfluxDBClient

from log.log import LOG

import signal
import time


class MetricsRunner(object):

  def __init__(self, props, exit_flag_event):
    self.props = props
    self.exit_flag_event = exit_flag_event
    self.influx_db_client = InfluxDBClient(
      self.props['metrics']['host'],
      self.props['metrics']['port'],
      self.props['metrics']['user'],
      self.props['metrics']['password'],
      self.props['metrics']['db']
    )
    self.lmsensors_metrics_thread = LmSensorsMetrics(
      influxdb_client=self.influx_db_client,
      exit_flag_event=self.exit_flag_event
    )
    self.nvidia_gpu_metrics_thread = NvidiaMetrics(
      influxdb_client=self.influx_db_client,
      exit_flag_event=self.exit_flag_event
    )

  def start_metrics_collection(self):
    self.lmsensors_metrics_thread.start()
    self.nvidia_gpu_metrics_thread.start()
    signal.pause()

  def stop_metrics(self):
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
