#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import OSConf
import rhtest
from quick_start_test import QuickStartTest

class QuickStartSqlbuddy(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["php"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: SQLBuddy"
        self.config.git_upstream_url = "git://github.com/openshift/sqlbuddy-openshift-quickstart.git"

        
    def verification(self):
        self.log_info("Verifying")
        app_url = OSConf.get_app_url(self.config.application_name)
        res = common.grep_web_page(app_url+'/sqlbuddy/login.php', 'Username')
        res += common.grep_web_page(app_url+'/sqlbuddy/login.php', 'Help!')
        self.assert_equal(res, 0, "All the patterns must be found")
        
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartSqlbuddy)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
