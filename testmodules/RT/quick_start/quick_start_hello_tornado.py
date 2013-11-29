#!/usr/bin/env python
import os, sys

import common
import rhtest
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartHelloTornado(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["diy"]
        self.config.application_embedded_cartridges = [  ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Hellotornado"
        self.config.git_upstream_url = "git://github.com/openshift/openshift-hellotornado.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Hello"
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartHelloTornado)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
