#!/usr/bin/env python
import os, sys

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
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types['ruby']
        self.allowed_app_name =  common.getRandomString(32)  #'ab012345678901234567890123456789'
        self.forbidden_app_name= common.getRandomString(33) #'abc012345678901234567890123456789'
        self.forbidden_domain_name = common.getRandomString(17)
        self.allowed_domain_name = common.getRandomString(16)
        self.current_domain_name = common.get_domain_name(self.user_email, self.user_passwd)
        tcms_testcase_id=122309
    	common.env_setup()
        self.steps_list = []

    def finalize(self):
        try:
            common.destroy_app(self.allowed_app_name)
            common.destroy_app(self.forbidden_app_name)
            os.system("rm -rf %s"%self.allowed_app_name)
            os.system("rm -rf %s"%self.forbidden_app_name)
        except:
            pass


class DomainAppNameLength(OpenShiftTest):
    def test_method(self):

        step = testcase.TestCaseStep("Create domain with namespace longer than 16",
                                  "rhc domain update %s %s -l %s -p '%s' %s" %(self.current_domain_name, self.forbidden_domain_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create app with name size - 32",
                                  common.create_app,
                                  function_parameters=[self.allowed_app_name, self.app_type, self.user_email, self.user_passwd, False],
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create app with name longer than 32",
                                  "rhc app create %s %s -l %s -p '%s' %s" %(self.forbidden_app_name, self.app_type, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)


        case = testcase.TestCase("Create domain and app whose name size is longer than maximum value",
                             self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DomainAppNameLength)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
