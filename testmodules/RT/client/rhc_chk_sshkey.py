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
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.key_filename= common.getRandomString(10)
        self.new_keyname = common.getRandomString(10)
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'
        tcms_testcase_id=129189
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        try:
            os.system("rm -f %s*"%self.key_filename)
            common.remove_sshkey(self.new_keyname, self.user_email, self.user_passwd)
        except:
            pass


class RhcChkSshkey(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep("Create a ssh key",
            "ssh-keygen -t dsa -f %s -N '' " % self.key_filename,
            expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Add this key to openshift" ,
            common.add_sshkey,
            function_parameters=["%s.pub" % (self.key_filename), self.new_keyname, self.user_email, self.user_passwd],
            expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Check the rhc domain status if throws eception" ,
            "eval `ssh-agent`; ssh-add ~/.ssh/id_rsa; rhc domain status -l %s -p '%s' %s"%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_return=0))

        case = testcase.TestCase("[US1652][UI][CLI] Multi key management rhc domain status",
                             self.steps_list)

        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcChkSshkey)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
