#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import OSConf
import rhtest
# user defined packages
from time import sleep
from quick_start_test import QuickStartTest

class QuickStartGollum(QuickStartTest):
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["ruby"]
        self.config.application_embedded_cartridges = [  ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: gollum"
        self.config.git_upstream_url = "git://github.com/openshift/gollum-openshifted.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Create New Page"
        
    def verification(self):
        self.log_info("Verifying")
        sleep(30) # Waiting 30 seconds before checking
        app_url = OSConf.get_app_url(self.config.application_name)
        ret_code = common.grep_web_page(
            "http://%s/" % app_url,
            self.config.page_pattern,
            options = "-L -H 'Pragma: no-cache' -u wiki:wiki"                                    
        )
        self.assert_equal(ret_code, 0, "Pattern %s must be found" % self.config.page_pattern)
 

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartGollum)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
