#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartTweetstream(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["jbossas"]
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Tweetstream"
        self.config.git_upstream_url = "git://github.com/openshift/tweetstream-example.git"
        self.config.page = "/pages/home.jsf"
        self.config.page_pattern = [ "TweetStream", "Top Tags", "Top Tweeters" ]
    
    def post_configuration_steps(self):
        self.log_info("Steps after configuration")
        properties_file = self.config.application_name + "/tweetstream/src/main/resources/twitter4j.properties"
        self.info("Editing file: " + properties_file)
        properties = open(properties_file, "w")
        properties.write("oauth.consumerKey=WYWyn60DsoDDkSmy3AGhw\n")
        properties.write("oauth.consumerSecret=uveHeAnasRBdJJevbl04P2nsqeZRxXM8HYqAyL2Vc\n")
        properties.write("oauth.accessToken=331629113-X53jKX8CcdgBxu1oqfx9dYBj8iEQ8wBuxjKiPok4\n")
        properties.write("oauth.accessTokenSecret=uTLdLwM5uoLepV4kyNUtPXUg0xc7MZKOeHBicBhw\n")
        properties.close()
    
    def pre_deployment_steps(self):
        self.log_info("Steps before deployments")
        steps = [
            "cd %s" % self.config.application_name,
            "git add .",
            "git commit -a -m configuration"
        ]
        common.command_get_status(" && ".join(steps))
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartTweetstream)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
