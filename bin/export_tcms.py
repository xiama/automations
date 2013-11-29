#!/usr/bin/env python

import database
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
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger

log = config_logger()
parser = OptionParser()


def config_parser():
    # these are required options.
    parser.add_option("-u", "--update", default='all', 
            help="update the tcms_tags table with the latest dump from TCMS")
    parser.add_option("-q", "--query", 
            help="query database to return testcases (tag_name|testcase_id) JSON string.")
    parser.add_option("-t", "--testcases", default='all', 
            help="'all' default to all testcases, <testcase_id> to update a specific testcase_id")
    parser.add_option("-c", action="store_true", dest="cases", 
            help="extract all testcase ids into a list")
    (options, args) = parser.parse_args()
    
    return options, args

if __name__ == '__main__':
    (options, args)= config_parser()
    
    if options.update:
        tcms = tcms_base.TCMS(test_plan='Test Plan for OpenShift 2.0')
        if options.update == 'all':
            # no name given then we update all tags
            tags, tags_obj = tcms.get_case_tags()
            for tag, tag_obj in zip(tags, tags_obj):
                log.info("Updating JSON for tag '%s'" % tag)
                database.populate_tcms_testcases_by_tag(tcms, tag_obj)
        else:
            name = options.update
            log.info("Updating JSON for tag '%s' in DB" % name)
            tag, tag_obj = tcms.get_case_tags(tag_name=name)
            database.populate_tcms_testcases_by_tag(tcms, tag_obj)

        
    elif options.query:
        try:
            case_id = int(options.query)
            testcase_dict = database.get_testcase_by_id(case_id)
            print testcase_dict
        except:
            tag_name = options.query
            tc_json = database.get_testcases_json_by_tag(tag_name)
            print tc_json
    elif options.testcases:
        tcms = tcms_base.TCMS(test_plan='Test Plan for OpenShift 2.0')
        if options.testcases == 'all':
            # update all testcases
            cases = tcms.get_testcases()
            for testcase in cases:
                res = database.populate_tcms_testcases(testcase, 
                        plan_id=tcms.plan_id)
        else:
            # just update a specific testcase id
            print "Not supported at this time"
            
    elif options.cases:
        res = database.get_all_tcms_testcases()
        print res
    else:
        pass
