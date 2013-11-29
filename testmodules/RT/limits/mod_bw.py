#!/usr/bin/env python
import os, sys

import testcase
import common
import rhtest

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types['php']
        self.file_size = 2048
        self.bw_limit = 500000
        tcms_testcase_id=122197

    	common.env_setup()
        self.steps_list = []

    def finalize(self):
        common.destroy_app(self.app_name)
        os.system("rm -Rf %s" % ( self.app_name ))


class ModBw(OpenShiftTest):
    def check_bandwidth(self, bandwidth):
        print "The download speed is: %s" % bandwidth
        if float(bandwidth) < self.bw_limit:
            return 0
        return 1

    def test_method(self):
        #1
        step = testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type],
            expect_description = "App should be created successfully",
            expect_return = 0)
        self.steps_list.append(step)

        #2
        step = testcase.TestCaseStep(
            "generate a %dK size file"% self.file_size,
            "dd if=/dev/zero bs=1K count=%d of=%s/php/tmp.html"% (self.file_size, self.app_name),
            expect_return = 0)
        self.steps_list.append(step)

        #3
        step = testcase.TestCaseStep(
            "Git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0)
        self.steps_list.append(step)

        #4
        step = testcase.TestCaseStep(
            "get app URL",
            common.get_app_url_from_user_info,
            function_parameters = [self.app_name])
        self.steps_list.append(step)

        #5
        step = testcase.TestCaseStep(
            "check feedback",
            "curl --fail --silent --max-time 300 -o /dev/null -w %{speed_download} -H 'Pragma: no-cache' __OUTPUT__[4]/tmp.html",
            expect_return = 0)
        self.steps_list.append(step)

        #6
        step = testcase.TestCaseStep(
            "check the bandwidth",
            self.check_bandwidth,
            function_parameters = ['__OUTPUT__[5]'],
            expect_return = 0)
        

        case = testcase.TestCase("[rhc-limits] apache bandwidth limit", self.steps_list)
        case.run()


        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ModBw)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
