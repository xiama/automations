#!/usr/bin/env python
import os, sys

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift
import common


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
	self.user_email = self.config.OPENSHIFT_user_email
    	self.user_passwd = self.config.OPENSHIFT_user_passwd
	self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'
        tcms_testcase_id = 141753

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class CreateAppWithoutDns(OpenShiftTest):
    def test_method(self):
	
        self.steps_list.append(testcase.TestCaseStep("Create a app without --no-dns",
                                  "rhc app create %s %s -l %s -p '%s' --no-git --no-dns %s"%(self.app_name, common.app_types[self.app_type], self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  unexpect_string_list=["Cloning into"],
                                  expect_return=0))

        case = testcase.TestCase("create an app with --no-dns option",
                             self.steps_list)

        def cleaning():
            cmd= "rhc app delete %s -l %s -p '%s' --confirm %s"%(self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
            common.command_get_status(cmd)

        case.add_clean_up(cleaning)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateAppWithoutDns)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
