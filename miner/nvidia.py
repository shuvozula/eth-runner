#!/usr/bin/env python

import logging

from miner.ethminer import EthMiner
from log.log import LOG, create_rotating_log_handler
from pynvml import nvmlDeviceGetCount


class NvidiaEthMiner(EthMiner):

  def __init__(self, props, influx_db_client, exit_flag_event):
    super(NvidiaEthMiner, self).__init__(props, influx_db_client, exit_flag_event)

  def __str__(self):
    return 'Ethminer-Nvidia'

  def _get_logger(self):
    return create_rotating_log_handler(
      log_file_location=self.props['ethminer']['nvidia']['miner_logs'],
      log_format=None,
      logger=logging.getLogger())

  def _tune_gpus(self):
    LOG.info('Enabling Nvidia cards...')
    self._run_subprocess('nvidia-xconfig --enable-all-gpus', LOG)

    LOG.info('Tuning Nvidia cards...')
    tune_script = 'nvidia-xconfig -a --cool-bits={cool_bits} --allow-empty-initial-configuration'.format(
      cool_bits=self.props['ethminer']['nvidia']['tuner']['cool_bits'])
    self._run_subprocess(tune_script, LOG)

  def _get_run_script(self):
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
    """.format({
      'path': self.props['ethminer']['path'],
      'farm_recheck': self.props['ethminer']['farm_recheck'],
      'stratum_client_version': self.props['ethminer']['stratum_client_version'],
      'cuda_parallel_hash': self.props['ethminer']['nvidia']['run']['cuda_parallel_hash'],
      'cuda_schedule': self.props['ethminer']['nvidia']['run']['cuda_schedule'],
      'cuda_devices': ' '.join(nvmlDeviceGetCount()),
      'stratum': self.props['ethminer']['stratum'],
      'stratum_failover': self.props['ethminer']['stratum_failover'],
      'account': self._get_account_id()
    })
