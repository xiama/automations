#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartFarmstand(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["nodejs"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mongodb"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Farmstand"
        self.config.git_upstream_url = "git://github.com/openshift/farmstand-nodejs-mongodb-example.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Find a Farm Stand"

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartFarmstand)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
