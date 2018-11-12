#!/usr/bin/env python

import logging
import subprocess

from ethminer import EthMiner
from log.log import LOG, create_rotating_log_handler


class AmdEthMiner(EthMiner):

  def __init__(self, props, influxdb_client, exit_flag_event):
    super(AmdEthMiner, self).__init__(props, influxdb_client, exit_flag_event)

  def __str__(self):
    return "Ethminer-AMD"

  def _get_run_script(self):
    self.props['ethminer']['amd'].update({
      'account': self._get_account_id(),

    })
    return """nohup {path}/ethminer \
      --farm-recheck {farm_recheck} \
      -SC {stratum_client_version} \
      --opencl-platform {opencl_platform_id} \
      -RH \
      -G \
      -S {stratum} \
      -FS {stratum_failover} \
      -O {account}
    """.format(self.props['ethminer']['amd'])

  def _stop_miner(self):
    LOG.info('Stopped AMD-Ethminer gracefully!')

  def _start_metrics(self):
    self.lmsensors_metrics.start()

  def _stop_metrics(self):
    pass
