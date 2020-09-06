#!/usr/bin/env python

from log.log import LOG
from miner import EthMiner


class AmdEthMiner(EthMiner):

    def __init__(self, props, influxdb_client, exit_flag_event):
        super(AmdEthMiner, self).__init__(props, influxdb_client, exit_flag_event)

    def __str__(self):
        return 'Ethminer-AMD'

    def _get_log_file_location(self):
        return self.props['ethminer']['amd']['miner_logs']

    def _tune_gpus(self):
        LOG.info("Nothing to tune for AMD GPUs as its already flashed with overclocked ROM...")

    def _get_run_script(self):
        return f"""nohup {self.props['ethminer']['path']}/ethminer \
              --farm-recheck {self.props['ethminer']['farm_recheck']} \
              -SC {self.props['ethminer']['stratum_client_version']} \
              --opencl-platform {self.props['ethminer']['amd']['opencl_platform_id']} \
              -RH \
              -G \
              -S {self.props['ethminer']['stratum']} \
              -FS {self.props['ethminer']['stratum_failover']} \
              -O {self._get_account_id()}
            """
