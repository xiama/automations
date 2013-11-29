#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common
import rhtest
from quick_start_test import QuickStartTest

class QuickStartNodeJSCustomVersion(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["nodejs"]
        self.config.application_nodejs_custom_version = "0.9.1"
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: NodeJS Custom Version"
        self.config.git_upstream_url = "git://github.com/openshift/nodejs-custom-version-openshift.git"
        self.config.page = "env"
        self.config.page_pattern = "Version: v" + self.config.application_nodejs_custom_version

    def post_configuration_steps(self):
        self.log_info("Post Configuration Steps")
        marker = open("./%s/.openshift/markers/NODEJS_VERSION" % self.config.application_name, "w")
        marker.write(self.config.application_nodejs_custom_version)
        marker.close()

    def pre_deployment_steps(self):
        self.log_info("Pre Deployment Steps")
        steps = [
            "cd %s" % self.config.application_name,
            "git commit -a -m NODEJS_VERSION"
        ]
        return common.command_get_status(" && ".join(steps))

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartNodeJSCustomVersion)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
