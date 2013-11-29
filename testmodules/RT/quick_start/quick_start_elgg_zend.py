#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
# user defined packages
from quick_start_elgg import QuickStartElgg

class QuickStartElggZend(QuickStartElgg):
    
    def __init__(self, config):
        QuickStartElgg.__init__(self, config)
        self.config.application_type = common.app_types["zend"]

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartElggZend)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
