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

  def _enable_nvidia_gpus(self, tuner_props):
    LOG.info('Enabling Nvidia cards...')

    self._run_subprocess('nvidia-xconfig --enable-all-gpus')

    self._run_subprocess("""nvidia-xconfig -a \
        --cool-bits={cool_bits} \
        --allow-empty-initial-configuration""".format(cool_bits=tuner_props['cool_bits']))

  def _tune_nvidia_gpus(self, tuner_props):
    LOG.info('Tuning Nvidia GPUs...')
    LOG.info(''.join(['='] * 43))
    LOG.info('Overclocking GPU Memory to ......... {mem_overclock}MHz'.format(**tuner_props))
    LOG.info('Overclocking GPU Processor to ...... {gpu_overclock}MHz'.format(**tuner_props))
    LOG.info('Under-powering to .................. {power_underclock}Watts'.format(**tuner_props))
    LOG.info(''.join(['='] * 43))

    gpu_overclock_args = []

    LOG.info('Tuning down power consumption...')
    for gpu_num in iter(nvmlDeviceGetCount()):

      # underclock the GPU power
      self._run_subprocess('nvidia-smi -i {gpu_num} -pl {power}'.format(
          gpu_num=gpu_num,
          power=tuner_props['power_underclock']))

      gpu_overclock_args.append(' \
        --assign [gpu:{gpu_num}]/GPUGraphicsClockOffset[3]={gpu_overclock} \
        --assign [gpu:{gpu_num}]/GPUMemoryTransferRateOffset[3]={mem_overclock}'.format(
            gpu_num=gpu_num,
            gpu_overclock=tuner_props['gpu_overclock'],
            mem_overclock=tuner_props['mem_overclock']
          ))

    # overclock the memory and underclock the processor
    LOG.info('Overclocking Nvidia GPU memory & processor...')
    self._run_subprocess('DISPLAY=:0 \
      XAUTHORITY=/var/run/lightdm/root/:0 \
      nvidia-settings {overclock_args}'.format(
          overclock_args=''.join(gpu_overclock_args)))

  def _tune_gpus(self):
    tuner_props = self.props['ethminer']['nvidia']['tuner']
    self._enable_nvidia_gpus(tuner_props)
    self._tune_nvidia_gpus(tuner_props)

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
    """.format(
        path=self.props['ethminer']['path'],
        farm_recheck=self.props['ethminer']['farm_recheck'],
        stratum_client_version=self.props['ethminer']['stratum_client_version'],
        cuda_parallel_hash=self.props['ethminer']['nvidia']['run']['cuda_parallel_hash'],
        cuda_schedule=self.props['ethminer']['nvidia']['run']['cuda_schedule'],
        cuda_devices=' '.join(iter(nvmlDeviceGetCount())),
        stratum=self.props['ethminer']['stratum'],
        stratum_failover=self.props['ethminer']['stratum_failover'],
        account=self._get_account_id())
