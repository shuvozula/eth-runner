#!/usr/bin/env python

import logging

from filters import ThreadLoggingFilter

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

file_logging_handler = None


def LoggingInit(log_path, log_filename, html=False):
  global LOG
  global file_logging_handler

  log_format = "[%(asctime)s %(threadName)s, %(levelname)s] %(message)s"
  file_name = "{0}/{1}.log".format(log_path, log_filename)

  if html:
    log_format = "<p>" + log_format + "</p>"
    file_name = "{0}/{1}.html".format(log_path, log_filename)

  log_formatter = logging.Formatter(log_format)

  file_logging_handler = logging.FileHandler(file_name)
  file_logging_handler.setFormatter(log_formatter)

  LOG.addHandler(file_logging_handler)
