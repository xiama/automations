#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)
tests_dir = sys.path.append([testdir,"/tests/"])

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
        self.max_procs = 250

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -Rf %s" % ( self.app_name ))


class Nproc(OpenShiftTest):
    def check_nproc(self, number):
        print "The max count of procs is: %s" % number
        if int(number) < self.max_procs:
            return 0
        return 

    def test_method(self):
        step = testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type],
            expect_description = "App should be created successfully",
            expect_return = 0)
        self.steps_list.append(step)
        tests_dir=os.path.join(testdir, "testmodules/RT/")
        
        step = testcase.TestCaseStep(
            "prepare template file",
            "cp -r %s/limits/app_template/* %s/php && sed -i -e 's/count.*\"/count %d\"/' %s/php/nproc.php"% (tests_dir, self.app_name, self.max_procs, self.app_name),
            expect_return = 0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep(
            "Git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep(
            "get app URL",
            common.get_app_url_from_user_info,
            function_parameters = [self.app_name])
        self.steps_list.append(step)

        #5
        step = testcase.TestCaseStep(
            "check feedback",
            "curl --fail --silent --max-time 300 -H 'Pragma: no-cache' __OUTPUT__[4]/nproc.php | grep max: | awk -F' ' '{ print $8 }'",
            expect_return = 0)
        self.steps_list.append(step)

        #6
        step = testcase.TestCaseStep(
            "check the number of processes",
            self.check_nproc,
            function_parameters = ['__OUTPUT__[5]'],
            expect_return = 0)
        step.add_clean_up(common.destroy_app, [self.app_name])
        self.steps_list.append(step)

        case = testcase.TestCase("[rhc-limits] numuber of processes limit", self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Nproc)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
