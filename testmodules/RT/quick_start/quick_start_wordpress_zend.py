#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartWordpressZend(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["zend"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge][US2812] quick-start example: Wordpress - with Zend Server"
        self.config.git_upstream_url = "git://github.com/openshift/wordpress-example.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Wordpress"
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartWordpressZend)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
