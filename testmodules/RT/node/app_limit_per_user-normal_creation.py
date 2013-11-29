import sys
import subprocess
import os
import string

import rhtest
import testcase
import common
import OSConf


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary= "Application limit per user validation on single/multiple node"
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types["php"]
        self.app_name_prefix = common.getRandomString(5)
        try:
            self.app_limit_per_user = string.atoi(os.environ["OPENSHIFT_app_limit_per_user"])
        except:
            self.info("Missing OPENSHIFT_app_limit_per_user, used 3 as default")
            self.app_limit_per_user=3

        self.app_name = "%s%s" %(self.app_name_prefix, self.app_limit_per_user + 1)
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s*" %self.app_name_prefix)
        common.destroy_app(self.app_name, self.user_email, self.user_passwd)
        case.add_clean_up("rm -rf %s"%(self.app_name))

class AppLimitPerUserNormalCreation(OpenShiftTest):

    def create_apps_one_by_one(self, start, end):
        for i in range(start, end + 1):
            app_name = "%s%s" %(self.app_name_prefix, i)
            ret = common.create_app(app_name, self.app_type, self.user_email, self.user_passwd)
            if ret != 0:
                print "---BAD---"
                break
        return ret
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create %s apps one by one according to app_limit_per_user setting" %(self.app_limit_per_user),
                self.create_apps_one_by_one,
                function_parameters=[1, self.app_limit_per_user],
                expect_return=0,
                expect_description="Apps should be created successfully"))

        self.steps_list.append(testcase.TestCaseStep(
                "Try to create one more app to validate app_limit_per_user",
                "rhc app create %s %s -l %s -p '%s' %s"
                    %(self.app_name, self.app_type, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return="!0",
                expect_string_list=["already reached the application limit of"],
                expect_description="No more app should be created"))


        case = testcase.TestCase(self.summary, self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppLimitPerUserNormalCreation)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
