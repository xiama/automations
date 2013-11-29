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
from jbossas_java6 import JBossJava6Test

class EAPScalingJava6Test(JBossJava6Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types["jbosseap"]
        self.config.git_repo = "./%s" % self.config.application_name
        self.config.scalable = True
        self.config.java_version = "1.6"
	self.config.summary = "[US2218] Java 6 with scaling EAP application"

    
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPScalingJava6Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

