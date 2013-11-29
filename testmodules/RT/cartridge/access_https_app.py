#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US537][rhc-cartridge] Access an SSL secured version of user's application
https://tcms.engineering.redhat.com/case/122433/
"""
import os,sys,re

import testcase,common,OSConf
import rhtest
#import database
# user defined packages
import openshift

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        try:
            self.test_variant = self.config.test_variant
        except:
            print "WARN: Missing OPENSHIFT_test_name, using php as default."
            self.test_variant = 'php'
        self.summary = "[US537][rhc-cartridge] Access an SSL secured version of user's application"

        self.app_name = "app"+self.test_variant
        self.app_type = common.app_types[self.test_variant]
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        pass

class AccessHttpsApp(OpenShiftTest):
    def test_method(self):
        # 1. Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Access app using http proto
        self.steps_list.append(testcase.TestCaseStep("2.Access app using http proto",
                common.grep_web_page,
                function_parameters=[self.get_app_url(self.app_name), "Welcome to OpenShift", "-H 'Pragma: no-cache'", 3, 4],
                expect_description="The app is available via http",
                expect_return=0))

        # 3.Access app using http proto
        self.steps_list.append(testcase.TestCaseStep("3.Access app using https proto",
                common.grep_web_page,
                function_parameters=[self.get_app_url(self.app_name, "https"), "Welcome to OpenShift", "-k -H 'Pragma: no-cache'", 3, 4],
                expect_description="The app is available via https",
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps_list)
        case.add_clean_up("rm -rf %s"%(self.app_name))

        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def get_app_url(self, app_name, proto="http"):
        def get_app_url2(): 
            return proto+"://"+OSConf.get_app_url(self.app_name)
        return get_app_url2


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AccessHttpsApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
