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

class EWSJava7Test(JBossJava7Test):

    def __init__(self, config):
        JBossJava7Test.__init__(self, config)
        self.config.application_type = common.app_types["jbossews"]
        self.config.git_repo = "./%s" % self.config.application_name
        self.config.summary = "[US2513] Java 7 with non-scaling JbossEWS application"
    
#    def deploy_version_checking_app(self):
#        os.mkdir(self.config.git_repo + "/webapps/testing/")
#        # Editing file
#        jsp_file = open(self.config.git_repo + "/webapps/testing/version.jsp", "w")
#        jsp_file.write('<%@ page contentType="text/plain" %>\n')
#        jsp_file.write('<%@ page trimDirectiveWhitespaces="true" %>\n')
#        jsp_file.write('<% out.println("Java version: " + System.getProperty("java.version")); %>\n')
#        jsp_file.close()
#        # Deploying
#        deployment_steps = [
#            "cd %s" % self.config.git_repo,
#            "git add .",
#            "git commit -a -m testing",
#            "git push"
#        ]
#        common.command_get_status(" && ".join(deployment_steps))
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSJava7Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

