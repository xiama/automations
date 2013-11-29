#!/usr/bin/env python

import tcms_base
import logging, logging.handlers
import sys
from optparse import OptionParser

def config_logger():
    # create formatter
    formatter = logging.Formatter("%(levelname)s [%(asctime)s] %(message)s",
            "%H:%M:%S")
    logger = logging.getLogger("dump_logs")
    log_formatter = logging.Formatter(
        "%(name)s: %(asctime)s - %(levelname)s: %(message)s")
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('out.log')

    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

log = config_logger()
parser = OptionParser()

def config_parser():
    # these are required options.
    parser.add_option("-t", "--testplan", default='Test Plan for OpenShift 2.0', 
            help="target testplan to update")
    parser.add_option("-a", "--action",  default='convert',
            help="action you want to take (convert|revert)")
    parser.add_option("-c", "--case_id", default=None, help="testcase id to be converted")
    (options, args) = parser.parse_args()
    
    return options, args

if __name__ == '__main__':
    (options, args)= config_parser()
    
    if options:
        testplan_name = options.testplan
        tcms_obj = tcms_base.TCMS(test_plan=testplan_name)
        if options.action == 'convert':
            tcms_base.update_script_field_to_json_format(tcms_obj, options.case_id)
            
        elif options.action == 'revert':
            tcms_base.revert_script_field_to_python_format(tcms_obj, options.case_id)
        else:
            log.info("No action defined, must be convert or revert") 
