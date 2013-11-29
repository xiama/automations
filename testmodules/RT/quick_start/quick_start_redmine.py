#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import OSConf
import rhtest
from quick_start_test import QuickStartTest

class QuickStartRedmine(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["ruby"]
        self.config.application_embedded_cartridges = [ common.cartridge_types['mysql'] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Redmine"
        self.config.git_upstream_url = "git://github.com/openshift/redmine-openshift-quickstart.git"
        self.config.page = "" # means '/'
        self.config.page_pattern = r"(Projects|Sign in|Redmine|Register)"
    
    def pre_configuration_steps(self):
        self.log_info("Pre-configuration steps...")
        steps = [
            "cd %s" % self.config.application_name,
            "rm -Rfv *"
        ]
        common.command_get_status(" && ".join(steps))
        
    def post_configuration_steps(self):
        self.log_info("Post-configuration steps...")
        mysql = OSConf.get_embed_info(self.config.application_name, common.cartridge_types['mysql'])
        steps = [
            "cd %s" % self.config.application_name,
            "sed -i -e 's/password:.*/password: %s/' -e 's/database: redmine/database: %s/' -e 's/host:.*/host: %s/' config/database.yml" % ( mysql["password"], self.config.application_name, mysql["url"] ) 
        ]
        common.command_get_status(" && ".join(steps))
    
    def pre_deployment_steps(self):
        self.log_info("Pre-deloyment steps...")
        steps = [
            "cd %s" % self.config.application_name,
            "git add .",
            "git commit -a -m db_changes"         
        ]
        common.command_get_status(" && ".join(steps))
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartRedmine)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
