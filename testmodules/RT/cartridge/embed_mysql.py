#!/usr/bin/env python
"""
Michal Zimen
jizhao@redhat.com
Apr 04, 2012
[rhc-cartridge] embed MySQL instance to RAW application
https://tcms.engineering.redhat.com/case/???/
"""
import os
import sys

import rhtest
import testcase
import common

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary ="[rhc-cartridge] embed MySQL instance to an application"
        try:
            self.app_type = common.app_types[self.config.test_variant]
        except:
            self.app_type = common.app_types["php"]
        self.app_name = "app4mysql"

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysql(OpenShiftTest):
    def test_method(self):
        mysql = common.cartridge_types['mysql']
        steps_list = []
        steps_list.append( testcase.TestCaseStep("Create a %s app" % (self.app_type), common.create_app, 
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        steps_list.append(testcase.TestCaseStep("Embed mysql to the app", 
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types['mysql']],
                expect_description="the mysql cartridge should be embedded successfully",
                expect_return=0))

        steps_list.append(testcase.TestCaseStep("Remove embedded mysql from the app", 
                common.embed,
                function_parameters=[self.app_name, "remove-" + common.cartridge_types['mysql']],
                expect_description="the mysql should be removed successfully",
                expect_return=0))


        case = testcase.TestCase(self.summary, steps_list)
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
    suite.add_test(EmbedMysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
