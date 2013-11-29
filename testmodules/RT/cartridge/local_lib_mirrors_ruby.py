#!/usr/bin/env python
"""
Linqing Lu
lilu@redhat.com
Dec 12, 2011

[US1343][Runtime][cartridge] Create local lib mirrors for Ruby framework
https://tcms.engineering.redhat.com/case/121925/
"""
import os,sys,re

import testcase, common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1343][Runtime][cartridge] Create local lib mirrors for Ruby framework"
        self.app = { 'name':'rubytest', 'type':common.app_types['ruby'] }
        self.steps_list =  []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app['name']))

class LocalLibMirrorsRuby(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
                "Create an %s app: %s" % (self.app['type'],self.app['name']),
                common.create_app,
                function_parameters = [self.app['name'], self.app['type']],
                expect_description = "App should be created successfully",
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                "Create new rails app",
                "rails new %s -f" % self.app['name'],
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                "Create new rails app, and bundle check",
                "cd %s && sed -i 's,rubygems.org,mirror1.prod.rhcloud.com/mirror/ruby,' Gemfile && bundle check" % self.app['name'],
                expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
                "Git push codes",
                "cd %s && git add . && git commit -am test && git push" % self.app['name'],
                expect_string_list = ['Installing rack', 'Fetching source index for http.*ruby'],
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
    suite.add_test(LocalLibMirrorsRuby)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
