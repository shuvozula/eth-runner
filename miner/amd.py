#!/usr/bin/env python

import logging

from miner.ethminer import EthMiner
from log.log import LOG, create_rotating_log_handler


class AmdEthMiner(EthMiner):

    def __init__(self, props, influxdb_client, exit_flag_event):
        super(AmdEthMiner, self).__init__(props, influxdb_client, exit_flag_event)

    def __str__(self):
        return 'Ethminer-AMD'

    def _get_logger(self):
        return create_rotating_log_handler(
            log_file_location=self.props['ethminer']['amd']['miner_logs'],
            log_format=None,
            logger=logging.getLogger())

    def _tune_gpus(self):
        LOG.info("Nothing to tune for AMD GPUs as its already flashed with overclocked ROM...")

    def _get_run_script(self):
        return """nohup {path}/ethminer \
      --farm-recheck {farm_recheck} \
      -SC {stratum_client_version} \
      --opencl-platform {opencl_platform_id} \
      -RH \
      -G \
      -S {stratum} \
      -FS {stratum_failover} \
      -O {account}
    """.format(
            path=self.props['ethminer']['path'],
            farm_recheck=self.props['ethminer']['farm_recheck'],
            stratum_client_version=self.props['ethminer']['stratum_client_version'],
            opencl_platform_id=self.props['ethminer']['amd']['opencl_platform_id'],
            stratum=self.props['ethminer']['stratum'],
            stratum_failover=self.props['ethminer']['stratum_failover'],
            account=self._get_account_id())
