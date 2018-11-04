#!/usr/bin/env python

import coloredlogs
import logging
import logging.handlers

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

LOG_MAX_BYTES = 100000000  # max log-file size of 100MB, until its rotated
LOG_BACKUP_COUNT = 5


def LoggingInit(log_path, log_filename, html=False):
  global LOG

  coloredlogs.install()

  log_format = "[%(asctime)s %(threadName)s, %(levelname)s] %(message)s"
  file_name = "{0}/{1}.log".format(log_path, log_filename)

  if html:
    log_format = "<p>" + log_format + "</p>"
    file_name = "{0}/{1}.html".format(log_path, log_filename)

  log_formatter = logging.Formatter(log_format)

  file_logging_handler = logging.handlers.RotatingFileHandler(file_name,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT)
  file_logging_handler.setFormatter(log_formatter)

  LOG.addHandler(file_logging_handler)
