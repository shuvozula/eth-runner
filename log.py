#!/usr/bin/env python

import logging


LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)


def LoggingInit(log_path, log_filename, html=False):
    global LOG

    log_format = "[%(asctime)s %(threadName)s, %(levelname)s] %(message)s"
    file_name = "{0}/{1}.log".format(log_path, log_filename)

    if html:
        log_format = "<p>" + log_format + "</p>"
        file_name = "{0}/{1}.html".format(log_path, log_filename)

    log_formatter = logging.Formatter(log_format)
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(log_formatter)
    LOG.addHandler(file_handler)
