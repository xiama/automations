#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartPiwik(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["php"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Piwik"
        self.config.git_upstream_url = "git://github.com/openshift/piwik-openshift-quickstart.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Piwik is an open source web analytics software that makes it easy to get the information you want from your visitors."
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartPiwik)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
