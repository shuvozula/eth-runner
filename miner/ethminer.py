#!/usr/bin/env python

import logging
import subprocess
import threading

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

    def _tune_gpus(self):
        raise NotImplementedError('Implement this to perform any GPU tuning.')

    def _get_run_script(self):
        raise NotImplementedError('Define the run-script for the ethminer process.')

    def _get_log_file_location(self):
        raise NotImplementedError('Define the log-file location for the ethminer process.')

    def _run_subprocess(self, run_script, logger=LOG):
        """
        Creates a subprocess.Popen() and logs the output to the provided logger. If the exit-flag-event
        gets set, then the subprocess is killed, otherwise keep logging until the subprocess finishes
        running.

        :param run_script:
        :param logger:
        :return:
        """
        LOG.debug('Launching subprocess "%s"', run_script)
        proc = subprocess.Popen(run_script,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=True)

        # keep running until the process has exited by itself, or the exit-flag-event is set
        LOG.debug('Logging output to %s', self._get_log_file_location())
        while proc.poll() is None and not self.exit_flag_event.is_set():
            logger.info(proc.stdout.readline())

        # if reached here, then ethminer process has stopped / needs to be stopped
        if self.exit_flag_event.is_set():
            LOG.info('Killing process %s...', str(proc))
            proc.kill()

        # pick up remaining logs in buffer
        logger.info(proc.communicate()[0])

    def run(self):
        self._tune_gpus()

        # Fetch the individual logger for the ethminer process
        ethminer_logger = create_rotating_log_handler(
            log_file_location=self._get_log_file_location(),
            log_format=None,
            logger=logging.getLogger())

        LOG.info('Launching %s...', str(self))

        self._run_subprocess(self._get_run_script(), ethminer_logger)  # blocking call
