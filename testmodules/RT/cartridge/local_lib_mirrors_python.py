#!/usr/bin/env python
"""
Linqing Lu
lilu@redhat.com
Dec 12, 2011

[US1309][rhc-cartridge]Create local lib mirrors for Python framework
https://tcms.engineering.redhat.com/case/122396/
"""
import os,sys,re
import rhtest
#import database
# user defined packages
import openshift

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase
import common

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1309][rhc-cartridge]Create local lib mirrors for Python framework"
        self.app = { 'name':'pythontest', 'type':common.app_types['python'] }
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s; "%(self.app['name']))

class LocalMirrorsPython(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app['type'],self.app['name']),
            common.create_app,
            function_parameters = [self.app['name'], self.app['type']],
            expect_description = "App should be created successfully",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                "Enable install_requires = ['Django>=1.3']",
                "sed -i '9s/^#//' %s/setup.py" % self.app['name'],
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                "Git push codes",
                "cd %s && git commit -am test && git push" % self.app['name'],
                expect_string_list = ['Installed.+Django', 'Reading http.*python'],
                expect_return = 0))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LocalMirrorsPython)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
