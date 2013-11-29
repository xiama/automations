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

class JBossJava7Test(rhtest.Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types["jbossas"]
        self.config.git_repo = "./%s" % self.config.application_name
        self.config.scalable = False
        self.config.java_version = "1.7"
	self.config.summary = "[US2218] Java 7 with non-scaling JBoss application"
    
    def log_info(self, message):
        self.info("========================")
        self.info(message)
        self.info("========================")

    def initialize(self):
        self.log_info("Initializing")
        common.env_setup()
        common.create_app(
            self.config.application_name,
            self.config.application_type,
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd,
            clone_repo = True,
            git_repo = self.config.git_repo,
            scalable = self.config.scalable
        )

    def finalize(self):
        self.log_info("Finalizing")
        rmtree(self.config.git_repo)

    def check_marker(self):
        self.assert_true("Marker must exist", os.path.exists(self.config.git_repo + "/.openshift/markers/java7"))

    def deploy_version_checking_app(self):
        # Editing file
        jsp_file = open(self.config.git_repo + "/src/main/webapp/version.jsp", "w")
        jsp_file.write('<%@ page contentType="text/plain" %>')
        jsp_file.write('<%@ page trimDirectiveWhitespaces="true" %>')
        jsp_file.write('<% out.println("Java version: " + System.getProperty("java.version")); %>')
        jsp_file.close()
        # Deploying
        deployment_steps = [
            "cd %s" % self.config.git_repo,
            "git add .",
            "git commit -a -m testing",
            "git push"
        ]
        common.command_get_status(" && ".join(deployment_steps))
        
    def test_method(self):
        self.check_marker()

        self.deploy_version_checking_app()

	sleep(30) # Waiting for the application

	number_of_operations = 1
	if self.config.scalable:
		number_of_operations = 3

	for i in range(0, number_of_operations):
            ret_code = common.check_web_page_output(
            	self.config.application_name, 
            	"version.jsp",
            	"Java version: " + self.config.java_version
            )
       	    self.assert_equal(ret_code, 0)

        # Everything is OK
        return self.passed(self.config.summary) 

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossJava7Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

