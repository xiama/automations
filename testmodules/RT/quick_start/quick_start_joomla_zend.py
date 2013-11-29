#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
# user defined packages
from quick_start_joomla import QuickStartJoomla

class QuickStartJoomlaZend(QuickStartJoomla):
    
    def __init__(self, config):
        QuickStartJoomla.__init__(self, config)
        self.config.application_type = common.app_types["zend"]

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartJoomlaZend)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
