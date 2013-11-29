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
        self.user_email = os.environ["OPENSHIFT_user_email"]
        self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.domain_name = common.get_domain_name()
        self.app_name="testapp"
        tcms_testcase_id=122313,122349
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass


class ClientNegativeTesting(OpenShiftTest):
    def test_method(self):
        step = testcase.TestCaseStep("rhc domain create Negative Testing: Without namespace",
                                  "rhc domain create -l %s -p '%s' %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=["Missing required argument 'namespace'"],
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc domain update Negative Testing: Invalid namespace",
                                  "rhc domain update %s '$$%%##' -l %s -p %s %s" % (self.domain_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=['Invalid namespace. Namespace must only contain alphanumeric characters'],
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Timeout Option Negative Testing: timeout value of string type",
                                 "rhc app create %s php-5.3 -l %s -p %s --timeout test %s --insecure" %(self.app_name, self.user_email, self.user_passwd),
                                 expect_string_list=['invalid argument: --timeout test'],
                                 expect_return="!0",
                                )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app create Negative Testing: Without app name",
                                  "rhc app create  -l %s -p %s %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=['Missing required argument \'name\''],
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app create Negative Testing: Invalid app name",
                                  "rhc app create '$#@*###' php-5.3 -l %s -p %s %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=['Invalid name specified'],
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app create Negative Testing: Without app type",
                                  "rhc app create myapp -l %s -p '%s' %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=['Every application needs a web cartridge'],
                                  expect_return="!0",
                                 )
        self.steps_list.append(step)


        if self.config.options.run_mode != 'DEV':
            step = testcase.TestCaseStep("rhc app create Negative Testing: Invalid app type",
                                      "rhc app create myapp php-test -l %s -p '%s' %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                      expect_string_list=['Invalid cartridge'],
                                      expect_return='!0'
                                     )
            self.steps_list.append(step)

        if self.config.options.run_mode != 'DEV':
            step = testcase.TestCaseStep("rhc app Negative Testing: non-existing application",
                                      "rhc app stop -a unexist -l %s -p %s %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                      expect_return='!0',
                                      expect_string_list=['Application unexist does not exist']
                                      #An application named \'unexist\' does not exist']
                                     )
            self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app Negative Testing: Invalid command",
                                  "rhc app haeel %s -l %s -p %s %s" %(self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return='!0',
                                  expect_string_list=['Too many arguments passed in.'],  # XXX need to update testcase once bug is fixed
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app Negative Testing: Without application",
                                  "rhc app show --state -l %s -p %s %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return='!0',
                                  expect_string_list=['Missing required argument \'app\'.']
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc app Negative Testing: Without command",
                                  "rhc app -a %s -l %s -p %s %s" %(self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return='!0',
                                  expect_string_list=['invalid option: -a'],
                                 )
        self.steps_list.append(step)

        if self.config.options.run_mode != 'DEV':
            step = testcase.TestCaseStep("'rhc snapshot save' Negative Testing: Invalid application",
                                     "rhc snapshot save -a unexist -l %s -p '%s' %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                     expect_return='!0',
                                     expect_string_list=['Application unexist does not exist']
                                    )
            self.steps_list.append(step)


            step = testcase.TestCaseStep("'rhc snapshot save' Negative Testing: Without app",
                                     "rhc snapshot save -l %s -p %s -a %s" %(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                     expect_return='!0',
                                     expect_string_list=['missing argument: -a']
                                    )
            self.steps_list.append(step)
#        self.steps_list.append(laststep)

        case = testcase.TestCase("[rhc-client]negative testing of client command including invalid option and miss argument\n[US1110][rhc-client]negative testing: give wrong value to --timeout option",
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
    suite.add_test(ClientNegativeTesting)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
