#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartOpenshiftWebpy(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["python"]
        self.config.application_embedded_cartridges = [  ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Openshiftwebpy"
        self.config.git_upstream_url = "git://github.com/openshift/openshiftwebpy.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "OpenShift"
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartOpenshiftWebpy)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
