#!/usr/bin/env python

from log.log import LOG

import os


class Watchdog(object):
  """
  Abstract base class for Watchdogs. Cannot be instantiated directly
  """

  def __init__(self):
    if type(self) is Watchdog:
      raise NotImplementedError('Abstract class cannot be directly instantiated!')

  def do_monitor(self, data):
    raise NotImplementedError('Abstract method needs to be overriden by derived class!')

  def switch_off_miner(self, wake_timeout_mins):
    """
    This issues a 'rtcwake' command to the underlying *nix system, with a sleep timeout
    of `wake_timeout_mins` seconds.

    Args:
      wake_timeout_mins: Minutes to sleep before waking up the system. Used with rtcwake.
    """
    LOG.warn('Shutting down miner for {} minutes...', wake_timeout_mins)
    os.system('sudo rtcwake -m off -s {}'.format(wake_timeout_mins * 60))
