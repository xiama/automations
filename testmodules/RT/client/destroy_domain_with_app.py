#!/usr/bin/env python
import os, sys
"""
testcase id 129353

"""
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift
lib_dir = os.path.join(testdir, "lib")

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        # check if there's a existing domain, create one if does not
        cf = self.config
        self.steps_list = []
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd

        self.info("Checking for existing domain...")
        status, res = cf.rest_api.domain_get()
        if status == 'OK':
            self.domain_name = res
            status, res = cf.rest_api.app_list()
            if len(res) > 0:
                # found an existing app, we are good to go.
                self.app_name = res[0]['name']
            else:
                self.info("Creating an app...")
                self.info("xxX", 1)
        else:
            self.info("No domain found, creating an new one...")
            self.info("xxx", 1)

    def finalize(self):
        pass


class DestroyDomainWithApp(OpenShiftTest):
    def test_method(self, args=None, case_id=None):
        step = testcase.TestCaseStep("Try to delete a domain with exisiting app(s)",
                "rhc domain delete %s -l %s -p '%s' %s"% (self.domain_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return="!0",
        )
        self.steps_list.append(step)

        case = testcase.TestCase("[US1653][RT][CLI] Try to destroy a domain with applications",
                self.steps_list 
                )
    	case.run()
	if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DestroyDomainWithApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
