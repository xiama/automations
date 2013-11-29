#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartLiferay(QuickStartTest):
        
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["jbossas"]
        self.config.application_embedded_cartridges = [ common.cartridge_types["mysql"] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: JBoss AS Liferay"
        self.config.git_upstream_url = "git://github.com/openshift/jbossas7-liferay-quickstart.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = "OpenShift"
    
    def initialize(self):
        self.log_info("Initializing")
        # General set-up
        common.env_setup()

        size = "medium"        
        # Changing node profile and VIP flag
        if self.get_run_mode() == "DEV":
            common.change_node_profile("medium")
            common.add_gearsize_capability('medium')
        elif self.get_run_mode() == "OnPremise":
            size = "small"
            
        # Creating the application
        common.create_app(
            self.config.application_name,
            self.config.application_type,
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd,
            clone_repo = True,
            git_repo = "./" + self.config.application_name,
            gear_size = size
        )
        
        # Embedding cartridges
        for cartridge in self.config.application_embedded_cartridges:
            common.embed(
                self.config.application_name,
                "add-" + cartridge,
                self.config.OPENSHIFT_user_email,
                self.config.OPENSHIFT_user_passwd
            )
        
    def post_deployment_steps(self):
        pass
        #sleep(120)
    
    def finalize(self):
        QuickStartTest.finalize(self)
        if self.get_run_mode() == "DEV":
            common.change_node_profile()
            common.remove_gearsize_capability('medium')
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartLiferay)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
