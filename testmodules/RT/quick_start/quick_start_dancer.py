#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartDancer(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self,config)
        self.config.application_type = common.app_types["perl"]
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: dancer"
        self.config.git_upstream_url = "git://github.com/openshift/dancer-example.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Perl is dancing"
    
    def pre_configuration_steps(self):
        self.log_info("Pre-onfiguring")
        steps = [
            "cd %s" % self.config.application_name,
            "rm -Rfv perl/",
            "git commit -a -m 'removing perl directory'"
        ]
        ret_code = common.command_get_status(" && ".join(steps))

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartDancer)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
