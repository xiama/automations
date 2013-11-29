'''
  File name: clog.py
  Date:      2012/09/11 15:09
  Author:    mzimen@redhat.com
'''

import os
import sys
import logging, logging.handlers

log=None

def _config_logger(level=logging.INFO):
    # create formatter
    formatter = logging.Formatter("%(levelname)s [%(asctime)s] %(message)s",
            "%H:%M:%S")
    logger = logging.getLogger("dump_logs")
    log_formatter = logging.Formatter(
        "%(name)s: %(asctime)s - %(levelname)s: %(message)s")
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    return logger



def get_logger():
    global log
    if log is None:
        level = logging.INFO
        if os.getenv('RHTEST_DEBUG'):
            level=logging.DEBUG
        log = _config_logger(level)
    return log

log = get_logger()

# end of clog.py 
