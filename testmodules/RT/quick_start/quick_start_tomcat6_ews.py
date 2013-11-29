#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartTomcatEWS(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["jbossews"]
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Tomcat6 (EWS)"
        self.config.git_upstream_url = "git://github.com/openshift/tomcat6-example.git"
        self.config.page = "hello"
        self.config.page_pattern = "Sample Application Servlet"

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartTomcatEWS)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
