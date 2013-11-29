#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
	self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_type = "perl-5.10"
        self.app_name = "testapp"
        tcms_testcase_id=98574

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass

class CreateTwoSameApp(OpenShiftTest):
    def test_method(self):

	step = testcase.TestCaseStep("Create the first app named %s" %(self.app_name),
                                  common.create_app,
                                  function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd, False],
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create the second app with the same name - %s" %(self.app_name),
                                  "rhc app create %s %s -l %s -p '%s' --no-git %s" %(self.app_name, self.app_type, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return="!0",
                                  expect_string_list=["already exists"],
                                 )
        self.steps_list.append(step)

        case = testcase.TestCase("Try to create two app with the same app",
                             self.steps_list
                            )
        case.run()
	

	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateTwoSameApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
