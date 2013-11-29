#!/usr/bin/python

"""
Attila Nagy
anagy@redhat.com

Jul 26, 2012
"""

import rhtest
import common
import os
from shutil import rmtree
from time import sleep
from jbossas_java7 import JBossJava7Test

class EAPJava7Test(JBossJava7Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types["jbosseap"]
        self.config.git_repo = "./%s" % self.config.application_name
        self.config.scalable = False
        self.config.java_version = "1.7"
	self.config.summary = "[US2218] Java 7 with non-scaling EAP application"
    
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPJava7Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

