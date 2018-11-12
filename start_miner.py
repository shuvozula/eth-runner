#!/usr/bin/env python

import argparse
import signal
import threading
import os
import sys
import time
import yaml

from influxdb import InfluxDBClient
from log.log import logging_init
from log.log import LOG
from nvidia.runner import NvidiaEthMiner
from amd.runner import AmdEthMiner


class EthRunner(object):

  def __init__(self, props):
    # register the kill handlers
    signal.signal(signal.SIGINT, self.stop)
    signal.signal(signal.SIGTERM, self.stop)

    # load the props
    with open(props, 'r') as f:
      self.props = yaml.safe_load(f)

    logging_init(self.props['logs']['location'], self.props['logs']['file_name'])

    self._create_pid()

    self.influx_db_client = InfluxDBClient(
      self.props['metrics']['host'],
      self.props['metrics']['port'],
      self.props['metrics']['user'],
      self.props['metrics']['password'],
      self.props['metrics']['db']
    )

    # to signal all threads to stop execution
    self.exit_flag_event = threading.Event()
    self.exit_flag_event.clear()

    # create the miner threads and share the exit-event handler
    self.nvidia_miner = NvidiaEthMiner(props, self.influx_db_client, self.exit_flag_event)
    self.amd_miner = AmdEthMiner(props, self.influx_db_client, self.exit_flag_event)

  def _create_pid(self):
    pid_file = os.path.join(self.props['pid_file']['location'],
                            self.props['pid_file']['file_name'])
    LOG.info('Creating pid file at %s with PID=[%s]...', pid_file, os.getpid())
    with open(pid_file, 'w') as f:
      f.write(str(os.getpid()))

  def __enter__(self):
    return self

  def tune_gpus(self):
    self.nvidia_miner.tune()

  def start(self):
    """
    Main entry point for the miner:
    1. Tune all the GPUs as applicable
    2. Start the miner threads (NVIDIA, AMD)
      a. Start the ethminers
      b. Start the watchdogs
      c. Start the metrics collectors
    """
    start_pause = long(self.props['ethrunner']['start_pause'])
    LOG.info('Sleeping for %d seconds before mining...', start_pause)
    time.sleep(start_pause)

    LOG.info('Tuning GPUS...')
    self.tune_gpus()

    LOG.info('Starting the Ethminers...')
    self.amd_miner.start()
    time.sleep(30)
    self.nvidia_miner.start()

    # wait for a kill event
    signal.pause()

  def stop(self):
    LOG.info('Stopping all metrics-collectors gracefully...')
    self.exit_flag_event.set()
    kill_timeout = float(self.props['ethrunner']['kill_timeout'])
    time.sleep(kill_timeout)

    while self.nvidia_miner.is_alive() and self.amd_miner.is_alive():
      LOG.error('Threads did not die within timeout %d seconds. Killing mining threads...', kill_timeout)
      self.nvidia_miner.join()
      self.amd_miner.join()

    sys.exit(0)


if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('--props', help="""
        Specify the path to where the app.yml configuration-file exists. Use the 
        metrics/apps.yml.sample to create an app.yml
        """)
  args = parser.parse_args()

  with EthRunner(args.props) as eth_runner:
    eth_runner.start()
