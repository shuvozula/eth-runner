#!/usr/bin/env python

from pynvml import nvmlDeviceGetCount

from log.log import LOG
from miner import EthMiner


class NvidiaEthMiner(EthMiner):

    def __init__(self, props, influx_db_client, exit_flag_event):
        super(NvidiaEthMiner, self).__init__(props, influx_db_client, exit_flag_event)

    def __str__(self):
        return 'Ethminer-Nvidia'

    def _get_log_file_location(self):
        return self.props['ethminer']['nvidia']['miner_logs']

    def _enable_nvidia_gpus(self, tuner_props):
        LOG.info('Enabling Nvidia cards...')

        self._run_subprocess('nvidia-xconfig --enable-all-gpus')

        self._run_subprocess(f"""nvidia-xconfig -a \
                --cool-bits={tuner_props['cool_bits']} \
                --allow-empty-initial-configuration""")

    def _tune_nvidia_gpus(self, tuner_props):
        LOG.info('Tuning Nvidia GPUs...')
        LOG.info(''.join(['='] * 43))
        LOG.info(f"Overclocking GPU Memory to ........ {tuner_props['mem_overclock']}MHz")
        LOG.info(f"Overclocking GPU Processor to ...... {tuner_props['gpu_overclock']}MHz")
        LOG.info(f"Under-powering to .................. {tuner_props['power_underclock']}Watts")
        LOG.info(''.join(['='] * 43))

        gpu_overclock_args = []

        LOG.info('Tuning down power consumption...')
        for gpu_num in iter(nvmlDeviceGetCount()):
            # underclock the GPU power
            self._run_subprocess(f"nvidia-smi -i {gpu_num} -pl {tuner_props['power_underclock']}")

            gpu_overclock_args.append(f" \
                --assign [gpu:{gpu_num}]/GPUGraphicsClockOffset[3]={tuner_props['gpu_overclock']} \
                --assign [gpu:{gpu_num}]/GPUMemoryTransferRateOffset[3]={tuner_props['mem_overclock']}")

        # overclock the memory and underclock the processor
        LOG.info('Overclocking Nvidia GPU memory & processor...')
        self._run_subprocess(f"DISPLAY=:0 \
              XAUTHORITY=/var/run/lightdm/root/:0 \
              nvidia-settings {''.join(gpu_overclock_args)}")

    def _tune_gpus(self):
        tuner_props = self.props['ethminer']['nvidia']['tuner']
        self._enable_nvidia_gpus(tuner_props)
        self._tune_nvidia_gpus(tuner_props)

    def _get_run_script(self):
        return f"""nohup {self.props['ethminer']['path']}/ethminer \
                --pool stratum://{self._get_account_id()}.miner@{self.props['ethminer']['stratum']} \
                --cuda \
                --report-hashrate \
                --farm-recheck {self.props['ethminer']['farm_recheck']} \

              --farm-recheck {self.props['ethminer']['farm_recheck']} \
              -SC {self.props['ethminer']['stratum_client_version']} \
              -RH \
              --cuda-parallel-hash {self.props['ethminer']['nvidia']['run']['cuda_parallel_hash']} \
              --cuda-schedule {self.props['ethminer']['nvidia']['run']['cuda_schedule']} \
              --cuda-devices {' '.join(iter(nvmlDeviceGetCount()))} \
              -U \
              -S {self.props['ethminer']['stratum']} \
              -FS {self.props['ethminer']['stratum_failover']} \
              -O {self._get_account_id()}
            """
