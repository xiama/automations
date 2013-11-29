#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
# user defined packages
from quick_start_test import QuickStartTest


class QuickStartDiyJavaDemo(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["diy"]
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Openshift-diy-java-demo"
        self.config.git_upstream_url = "git://github.com/openshift/openshift-diy-java-demo.git"
        self.config.random_string = common.getRandomString()
        self.config.page = "test.html"
        self.config.page_pattern = self.config.random_string
        
    def post_configuration_steps(self):
        self.log_info("Steps after configuration")
        print "Creating test.html file"
        test_html = open("%s/html/test.html" % self.config.application_name, "w")
        test_html.write("<html>\n")
        test_html.write("<head><title>Testing</title></header>\n")
        test_html.write("<body><p>%s</p></body\n>" % self.config.random_string)
        test_html.write("</html>\n")
        test_html.close()
        
    def pre_deployment_steps(self):
        self.log_info("Step before deploying")
        steps = [
            "cd %s" % self.config.application_name,
            "git add .",
            "git commit -a -m testing"     
        ]
        ret_code = common.command_get_status(" && ".join(steps))
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartDiyJavaDemo)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
