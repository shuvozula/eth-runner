#!/usr/bin/env python

from log.log import LOG
from watchdog import Watchdog


# Maximum heat limit per AMD GPU allowed
HEAT_LIMIT = 70

# Minutes to sleep after killing the miners if something is found wrong with the GPUs
SLEEP_TIMEOUT_MINS = 20


class LmSensors(Watchdog):
    """
    Monitors the AMD GPUs and their temperatures to make sure they dont overheat.
    TODO: Add more checks as required, eg: CPU core temperatures, etc.
    """

    def __init__(self, exit_flag_event):
        super(LmSensors, self).__init__(exit_flag_event)
        LOG.info("LmSensors-Watchdog started!")

    def do_monitor(self, data_list):
        for data in data_list:
            if 'gpu' in data['tags'].keys():
                device_name = data['measurement']
                amd_gpu_temperature = data['fields']['temperature']

                if amd_gpu_temperature > HEAT_LIMIT:
                    LOG.error('Current temperature of AMD GPU-%s is %d > %d! Killing all miners...',
                              device_name, amd_gpu_temperature, HEAT_LIMIT)
                    self.switch_off_miner(SLEEP_TIMEOUT_MINS)