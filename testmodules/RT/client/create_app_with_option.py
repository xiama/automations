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
        self.app_repo = "/tmp/%s_repo" %(self.app_name)
        tcms_testcase_id= 154268,142464
    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class CreateAppWithOption(OpenShiftTest):
    def test_method(self):

        step = testcase.TestCaseStep("Create app with -n option",
                                  common.create_app,
                                  function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd, False],
                                  expect_return=0,
                                  expect_string_list=["no local repo has been created"],
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check git repo dir",
                                  "ls %s" %(self.app_name),
                                  expect_return="!0",
                                  expect_string_list=["No such file or directory"],
                                  expect_description="There should no git repo dir"
                                 )
        step.add_clean_up(common.destroy_app, [self.app_name, self.user_email, self.user_passwd])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Clean targe path to prepare the next test",
                                  "rm -rf %s && ls %s" %(self.app_repo, self.app_repo),
                                  expect_return="!0",
                                  expect_string_list=["No such file or directory"],
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create app with -r option",
                                  common.create_app,
                                  function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd, True, self.app_repo],
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check git repo is cloned to specified path",
                                  "ls %s" %(self.app_repo),
                                  expect_return=0
                                 )
        step.add_clean_up("rm -rf %s" %(self.app_repo))
        self.steps_list.append(step)

        case = testcase.TestCase("Create app with -n/-r option",
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
    suite.add_test(CreateAppWithOption)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
