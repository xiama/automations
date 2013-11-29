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
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types['php']
        self.file_size_limit = 1048576
        tcms_testcase_id=122321
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -Rf %s" % ( self.app_name ))


class FileCapacity(OpenShiftTest):
    def test_method(self):

        step=testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, 
                                   self.app_type, 
                                   self.config.OPENSHIFT_user_email,
                                   self.config.OPENSHIFT_user_passwd,
                                   True],
            expect_description = "App should be created successfully",
            expect_return = 0)
        self.steps_list.append(step)

        every_cap = 500000
        left_limit = self.file_size_limit
        i = 0
        while left_limit > 0:
            if left_limit > every_cap:
                step = testcase.TestCaseStep(
                    "generate a %dK size file"% every_cap,
                    "dd if=/dev/zero bs=1K count=%d of=%s/bigfile%s"% (every_cap, self.app_name, i),
                    expect_return = 0)
                self.steps_list.append(step)

                step = testcase.TestCaseStep(
                    "Git push codes",
                    "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
                    expect_return = 0,
                    unexpect_string_list = ['Disk quota exceeded'])
                    #expect_string_list = ['remote rejected'])
                self.steps_list.append(step)
            else:
                step = testcase.TestCaseStep(
                    "generate a %dK size file" %(left_limit),
                    "dd if=/dev/zero bs=1K count=%d of=%s/bigfile%s" %(left_limit, self.app_name, i),
                    expect_return = 0)
                self.steps_list.append(step)

                step = testcase.TestCaseStep(
                    "Git push codes",
                    "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
                    expect_string_list = ['Disk quota exceeded'])
                    #expect_string_list = ['remote rejected'])
                self.steps_list.append(step)


            left_limit = left_limit - every_cap
            i = i + 1

        step=testcase.TestCaseStep(
            "Destroy app: %s" % (self.app_name),
            common.destroy_app,
            function_parameters = [self.app_name],
            expect_return = 0)
        self.steps_list.append(step)
    
        case = testcase.TestCase("[rhc-limits] file size limit", self.steps_list)
        case.run()
        
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(FileCapacity)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
