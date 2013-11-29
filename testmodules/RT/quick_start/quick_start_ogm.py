#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartOGM(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["jbossas"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mongodb"]]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: OGM"
        self.config.git_upstream_url = "git://github.com/openshift/openshift-ogm-quickstart.git"
        self.config.page = "index.jsf"
        self.config.page_pattern = "Welcome to OGM Kitchensink demo!"

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartOGM)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
