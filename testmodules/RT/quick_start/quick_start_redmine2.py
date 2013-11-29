#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest


class QuickStartRedmine2(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["ruby"]
        self.config.application_embedded_cartridges = [ common.cartridge_types['mysql'] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Redmine 2.0"
        self.config.git_upstream_url = "git://github.com/openshift/redmine-2.0-openshift-quickstart.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = r"(Projects|Sign in|Redmine|Register)"
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartRedmine2)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
