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

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rhc domain delete %s -l %s -p '%s' %s"% (self.domain_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        os.system("rm -rf /tmp/OPENSHIFT_OSConf-%s.dump"%self.user_email)


class AppsCleanUp(OpenShiftTest):
    def test_method(self):
        step = testcase.TestCaseStep("Re-inintilize OSConf file",
                    OSConf.initial_conf,
                    function_parameters=[],
                    expect_return=0
        )
        self.steps_list.append(step)
        
        step = testcase.TestCaseStep("Clean all the apps of the user",
                    common.clean_up,
                    function_parameters=[self.user_email, self.user_passwd],
                    expect_return=0)
        self.steps_list.append(step)

        ''' MOVED TO FINALIZE()....
        step = testcase.TestCaseStep("Destroy domain namesplace",
                    "rhc domain delete %s -l %s -p %s"% (self.domain_name, self.user_email, self.user_passwd),
                    expect_return=0)
        self.steps_list.append(step)
        
        step = testcase.TestCaseStep("Clean OSConf dump file",
                    "rm -rf /tmp/OPENSHIFT_OSConf-%s.dump"%self.user_email,
                    expect_return=0)
        self.steps_list.append(step)
        '''

        case = testcase.TestCase("Clean all the apps of the user", self.steps_list)
        case.run()


        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppsCleanUp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
