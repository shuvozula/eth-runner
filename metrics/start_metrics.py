#!/usr/bin/env python

# TODO:Remove this block later
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collect_amd_cpu_metrics import LmSensorsMetrics
from collect_nvidia_metrics import NvidiaMetrics
from influxdb import InfluxDBClient

from log.log import logging_init
from log.log import LOG

import argparse
import signal
import threading
import time
import yaml


class MetricsRunner(object):

  def __init__(self):
    signal.signal(signal.SIGINT, self._kill_callback)
    signal.signal(signal.SIGTERM, self._kill_callback)

    parser = argparse.ArgumentParser()
    parser.add_argument('--props', type=basestring, help="""
        Specify the path to where the app.yml configuration-file exists. Use the 
        metrics/apps.yml.sample to create an app.yml
        """)
    args = parser.parse_args()

    with open(args.props, 'r') as f:
      self.props = yaml.safe_load(f)

    logging_init(self.props['logs']['location'], self.props['logs']['file_name'])

    pid_file = os.path.join(self.props['pid_file']['location'],
                            self.props['pid_file']['file_name'])
    LOG.info('Creating pid file at %s with PID=[%s]...', pid_file, os.getpid())
    with open(pid_file, 'w') as f:
      f.write(str(os.getpid()))

  def __enter__(self):
    self.exit_flag_event = threading.Event()
    self.exit_flag_event.clear()
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
