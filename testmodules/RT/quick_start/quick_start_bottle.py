#!/usr/bin/env python

import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
# user defined packages
from quick_start_test import QuickStartTest


class QuickStartBottle(QuickStartTest):
      
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types['python']
        self.config.application_embedded_cartridges = [ ] # Not Needed
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Bottle"
        self.config.git_upstream_url = "git://github.com/openshift/bottle-openshift-quickstart.git"
        self.config.page = "/"
        self.config.page_pattern = "Hello World!"

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartBottle)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
