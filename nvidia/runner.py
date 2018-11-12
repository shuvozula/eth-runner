#!/usr/bin/env python

import os
import subprocess
import time

from log.log import LOG
from ethminer import EthMiner


class NvidiaEthMiner(EthMiner):

  def __init__(self, props, influx_db_client, exit_flag_event):
    super(NvidiaEthMiner, self).__init__(props, influx_db_client, exit_flag_event)

  def tune(self):
    self._enable_nvidia()
    self._tune_gpus()

  def _enable_nvidia(self):
    LOG.info('Enabling Nvidia cards...')

    pass

  def _tune_gpus(self):
    LOG.info('Tuning Nvidia cards...')
    gpu_tune_proc = subprocess.Popen('nvidia-xconfig --enable-all-gpus',
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    for line in iter(gpu_tune_proc.stdout.readline, ''):
      LOG.info(line)
    gpu_cool_bits = subprocess.Popen('nvidia-xconfig -a --cool-bits={cool_bits} --allow-empty-initial-configuration'.format(
      cool_bits=self.props['']))

  def _get_run_script(self):
    self.props['ethminer']['nvidia'].update({
      'account': self._get_account_id(),
      
    })
    return """nohup {path}/ethminer \
    --farm-recheck {farm_recheck} \
    -SC {stratum_client_version} \
    -RH \
    --cuda-parallel-hash {cuda_parallel_hash} \
    --cuda-schedule {cuda_schedule} \
    --cuda-devices {cuda_devices} \
    -U \
    -S {stratum} \
    -FS {stratum_failover} \
    -O {account}
    """.format(self.props['ethminer']['nvidia'])
