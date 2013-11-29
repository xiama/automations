#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartOwnCloud(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["php"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Own Cloud"
        self.config.git_upstream_url = "git://github.com/openshift/owncloud-openshift-quickstart.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "index.php"
        #self.config.page_pattern = "ownCloud"

    def pre_configuration_steps(self):
        self.log_info("Pre Configuration Steps")
        os.remove("./%s/php/index.php" % self.config.application_name)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartOwnCloud)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
