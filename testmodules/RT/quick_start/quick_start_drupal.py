#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartDrupal(QuickStartTest):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["php"]
        self.config.application_embedded_cartridges = [ common.cartridge_types['mysql'] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: drupal"
        self.config.git_upstream_url = "git://github.com/openshift/drupal-example.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Welcome to OpenShift Drupal"
   

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartDrupal)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
