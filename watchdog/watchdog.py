#!/usr/bin/env python

import os
import time

from datetime import datetime, timedelta
from log.log import LOG


class Watchdog(object):
  """
  Abstract base class for Watchdogs. Cannot be instantiated directly
  """

  def __init__(self, exit_flag_event, timeout_seconds):
    if type(self) is Watchdog:
      raise NotImplementedError('Abstract class cannot be directly instantiated!')
    self._exit_flag_event = exit_flag_event
    self.start_monitor_time = datetime.now() + timedelta(0, timeout_seconds)
    self.power_switchoff_threshold = 5
    self.heat_switchoff_threshold = 2

  def monitor(self, data):
    if datetime.now() > self.start_monitor_time:
      self.do_monitor(data)

  def do_monitor(self, data):
    raise NotImplementedError('Abstract method needs to be overriden by derived class!')

  def switch_off_miner_overheat(self, wake_timeout_mins):
    self.heat_switchoff_threshold -= 1
    if self.heat_switchoff_threshold <= 0:
      self.switch_off_miner(wake_timeout_mins)

  def switch_off_miner_underpowered(self, wake_timeout_mins):
    self.power_switchoff_threshold -= 1
    if self.power_switchoff_threshold <= 0:
      self.switch_off_miner(wake_timeout_mins)

  def switch_off_miner(self, wake_timeout_mins):
    """
    This issues a 'rtcwake' command to the underlying *nix system, with a sleep timeout
    of `wake_timeout_mins` seconds.

    Args:
      wake_timeout_mins: Minutes to sleep before waking up the system. Used with rtc-wake.
    """
    LOG.warn('Abnormality found!! Shutting down miner!')

    LOG.warn('Signalling metrics-threads for shutdown sequence...')
    self._exit_flag_event.set()
    time.sleep(65)

    LOG.warn('Going to sleep for %d minutes...', wake_timeout_mins)
    time.sleep(30)
    os.system('sudo rtcwake -m off -s {}'.format(wake_timeout_mins * 60))
