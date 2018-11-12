#!/usr/bin/env python

import subprocess
import threading

import logging
from log.log import LOG, create_rotating_log_handler


class EthMiner(threading.Thread):

  def __init__(self, props, influx_db_client, exit_flag_event):
    threading.Thread.__init__(self)

    if type(self) is EthMiner:
      raise NotImplementedError('Abstract class cannot be directly instantiated')

    self.props = props
    self.influx_db_client = influx_db_client
    self.exit_flag_event = exit_flag_event

  def _get_account_id(self):
    with open(self.props['ethminer']['account_file']) as account_file:
      return account_file.read()

  def _get_run_script(self):
    raise NotImplementedError('Needs to be implemented by derived class.')

  def _stop_miner(self):
    raise NotImplementedError('Needs to be implemented by derived class.')

  def run(self):
    LOG.info('Launching %s...', str(self))
    self.ethminer_logger = create_rotating_log_handler(
      log_file_location=self.props['ethminer']['amd']['miner_logs'],
      log_format=None,
      logger=logging.getLogger())
    self.ethminer_process = subprocess.Popen(
      self._get_run_script(),
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)
    while self.ethminer_process.poll() is None and not self.exit_flag_event.is_set():
      self.ethminer_logger.info(self.ethminer_process.stdout.readline())

  def stop(self):
