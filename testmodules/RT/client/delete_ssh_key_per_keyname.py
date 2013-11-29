#!/usr/bin/env python
import os, sys

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


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
	self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
	self.key_filename="my_testing_second_key"
	self.new_keyname="second"
        tcms_testcase_id=129355
    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class DeleteSshKeyPerKeyname(OpenShiftTest):
    def cleanup(self):
        os.system("rm -f %s*" % (self.key_filename))
        common.remove_sshkey(self.new_keyname, self.user_email, self.user_passwd)

    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep(
            "Just for sure from previus testing... - remove that key file",
            self.cleanup))

        self.steps_list.append(testcase.TestCaseStep("Create additional key" ,
            "ssh-keygen -t dsa -f %s -N '' " % self.key_filename,
            expect_return=0))

        self.steps_list.append(testcase.TestCaseStep(
            "Add this key to openshift" ,
            common.add_sshkey,
            function_parameters=["%s.pub" % (self.key_filename), self.new_keyname, self.user_email, self.user_passwd],
            expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Remove that key",
            common.remove_sshkey,
            function_parameters=[self.new_keyname, self.user_email, self.user_passwd],
            expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Check the presence of the key in the list",
            "rhc sshkey list -l %s -p '%s' %s | grep -i 'Name: %s' "%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS, self.new_keyname),
            expect_return="!0"))

        self.steps_list.append(testcase.TestCaseStep("Remove that non-existing key",
            common.remove_sshkey,
            function_parameters=[self.new_keyname, self.user_email, self.user_passwd],
            expect_string_list = ["Key name 'X%sX' doesn't exist for user %s" %(self.new_keyname, common.raw_str(self.user_email))],
            expect_return="!0"))

        case = testcase.TestCase("[US1652][UI][CLI]delete a ssh key with existing specific key-name",
            steps=self.steps_list)

        case.add_clean_up(self.cleanup)
        case.run()


	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DeleteSshKeyPerKeyname)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
