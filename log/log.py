#!/usr/bin/env python

import coloredlogs
import logging
import logging.handlers

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

LOG_FORMAT = "[%(asctime)s %(threadName)s, %(levelname)s] %(message)s"
LOG_MAX_BYTES = 100000000  # max log-file size of 100MB, until its rotated
LOG_BACKUP_COUNT = 5


def logging_init(log_file_location, html=False):
    """
    Initializes the LOG object for global logging, which is a rotating log-handler:
    creates max of LOG_BACK_COUNT log files; older ones are deleted, with each log
    file of size LOG_MAX_BYTES. Can be configured to log HTML or text, defaults to text.

    :param log_file_location:
    :param html:
    :return:
    """
    global LOG

    log_format = LOG_FORMAT
    if html:
        log_format = "<p>" + LOG_FORMAT + "</p>"

    LOG = create_rotating_log_handler(
        log_file_location=log_file_location,
        log_format=log_format)

    coloredlogs.install(logger=LOG)


def create_rotating_log_handler(log_file_location,
                                log_format=LOG_FORMAT,
                                logger=LOG,
                                max_bytes=LOG_MAX_BYTES,
                                back_up_count=LOG_BACKUP_COUNT):
    """
    Creates a rotating log handler using the provided max_bytes and the back_up_count of logs to keep
    at log_file_location

    :param log_file_location:
    :param log_format:
    :param logger:
    :param max_bytes:
    :param back_up_count:
    :return:
    """
    file_logging_handler = logging.handlers.RotatingFileHandler(log_file_location,
                                                                maxBytes=max_bytes,
                                                                backupCount=back_up_count)
    if log_format:
        log_formatter = logging.Formatter(log_format)
        file_logging_handler.setFormatter(log_formatter)

    logger.addHandler(file_logging_handler)

    return logger
