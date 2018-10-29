#!/usr/bin/env python

import threading
import logging

thread_local = threading.local()

class ThreadLoggingFilter(logging.Filter):
  def __init__(self, thread):
    self.thread = thread 

  def filter(self, record):
    record.method = thread_local.request.method
    record.ip = thread_local.request.ip
    # record.appName = appName = thread_local.appName
    return True
