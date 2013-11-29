#!/usr/bin/env python
import os, sys

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift
import subprocess

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types['php']
        self.file_count_limit = 40000
        tcms_testcase_id=122322
    	common.env_setup()
        self.steps_list = []

    def finalize(self):
        common.destroy_app(self.app_name)
        os.system("rm -rf %s"%self.app_name)


class FileCount(OpenShiftTest):

    def gen_files(self):
        for i in range(0, self.file_count_limit):
            retcode = subprocess.call(''.join(["touch %s/tmp."%self.app_name, str(i)]), shell=True)
        return retcode

    def test_method(self):

        step = testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type],
            expect_description = "App should be created successfully",
            expect_return = 0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep(
            "generate %s files"% self.file_count_limit,
            self.gen_files,
            expect_return = 0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep(
            "Git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_string_list = ['Disk quota exceeded'])
#            expect_return = 0)


        case = testcase.TestCase("[rhc-limits] file count limit", self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(FileCount)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
