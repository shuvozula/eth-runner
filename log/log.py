#!/usr/bin/env python

import coloredlogs
import logging
import logging.handlers

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

LOG_MAX_BYTES = 100000000  # max log-file size of 100MB, until its rotated
LOG_BACKUP_COUNT = 5


def logging_init(log_path, log_filename, html=False):
  """
  Initializes the LOG object for global logging, which is a rotating log-handler:
  creates max of LOG_BACK_COUNT log files; older ones are deleted, with each log
  file of size LOG_MAX_BYTES. Can be configured to log HTML or text, defaults to text.
  """
  global LOG

  log_format = "[%(asctime)s %(threadName)s, %(levelname)s] %(message)s"
  file_name = "{0}/{1}.log".format(log_path, log_filename)

  if html:
    log_format = "<p>" + log_format + "</p>"
    file_name = "{0}/{1}.html".format(log_path, log_filename)

  coloredlogs.install(
    level='DEBUG',
    logger=LOG,
    fmt=log_format
  )

  log_formatter = logging.Formatter(log_format)

  file_logging_handler = logging.handlers.RotatingFileHandler(file_name,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT)
  file_logging_handler.setFormatter(log_formatter)

  LOG.addHandler(file_logging_handler)
