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

class JBossJava6Test(JBossJava7Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types["jbossas"]
        self.config.git_repo = "./%s" % self.config.application_name
        self.config.scalable = False
        self.config.java_version = "1.6"
	self.config.summary = "[US2218] Java 6 with non-scaling JBoss application"

    def check_marker(self):
	marker_file_name = self.config.git_repo + "/.openshift/markers/java7"
        if os.path.exists(marker_file_name):
	    os.remove(marker_file_name)
    
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossJava6Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

