#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com

"""
import os, sys

import common
import rhtest
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartJuvia(QuickStartTest):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["ruby-1.9"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Juvia - with Ruby 1.9"
        self.config.git_upstream_url = "git://github.com/openshift/juvia-example.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Welcome to Juvia"
        
    def post_configuration_steps(self):
        steps = [
            "cd %s" % self.config.application_name,
            "sed -i -e 's/\$app/%s/g' -e 's/\$domain/%s/g' config/application.yml" % ( self.config.application_name, common.get_domain_name() ),
        ]
        ret_code = common.command_get_status(" && ".join(steps))
        self.assert_equal(ret_code, 0, "Post-configuration step must be successful")
        
    def pre_deployment_steps(self):
        steps = [
            "cd %s" % self.config.application_name,
            "git commit -a -m custom_configuration"  
        ]
        ret_code = common.command_get_status(" && ".join(steps))
        self.assert_equal(ret_code, 0, "Post-configuration steps must be successful")
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartJuvia)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
