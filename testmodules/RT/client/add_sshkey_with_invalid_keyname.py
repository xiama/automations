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
        self.key_filename="my_testing_second_key"
        self.key_filename2="my_testing_second_key2"
        self.key_filename3="my_testing_second_key3"
        self.new_keyname="second"
        self.invalid_keyname="*%^+"
        tcms_testcase_id = 129354
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        pass


class AddSshKeyWithInvalidKeyname(OpenShiftTest):
    def cleanup(self):
        os.system("rm -f %s*" % (self.key_filename))
        common.remove_sshkey(self.new_keyname, self.user_email, self.user_passwd)

    def test_method(self):
        self.steps_list.append( testcase.TestCaseStep("Just for sure from previus testing... - remove that key",
                                self.cleanup,
                              ))

        self.steps_list.append(testcase.TestCaseStep("Create additional key" ,
                                  "ssh-keygen -t dsa -f %s -N '' " % self.key_filename,
                                  expect_return=0
                                 ))

        self.steps_list.append(testcase.TestCaseStep("Add this key to openshift" ,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_filename), self.new_keyname, self.user_email, self.user_passwd],
                                  expect_return=0
                                 ))
        #this key shouldn't be added, because of
        self.steps_list.append(testcase.TestCaseStep("Create 2nd additional key" ,
                                  "ssh-keygen -t dsa -f %s -N '' " % self.key_filename2,
                                  expect_return=0
                                 ))

        self.steps_list.append(testcase.TestCaseStep("Add second key this key to openshift" ,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_filename2), self.new_keyname, self.user_email, self.user_passwd],
                                  expect_description="Should fail, because of duplicates",
                                  expect_return="!0",
                                 ))

        self.steps_list.append(testcase.TestCaseStep("Add second key this key to openshift with invalid key-name" ,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_filename2), self.invalid_keyname, self.user_email, self.user_passwd],
                                  expect_description="Should fail, because of invalid keyname",
                                  expect_return="!0",
                                 ))


        #check for the key type
        self.steps_list.append(testcase.TestCaseStep("Create additional fake key",
                                  "echo 'key' >%s.pub " % self.key_filename3,
                                  expect_return=0
                                 ))

        self.steps_list.append(testcase.TestCaseStep("Add this key to openshift" ,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_filename3), "fake", self.user_email, self.user_passwd],
                                  expect_return="!0",
                                 ))

        case = testcase.TestCase("[US1652][UI][CLI]add a ssh key with invalid or existing key-name",
                             steps=self.steps_list
                            )

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
    suite.add_test(AddSshKeyWithInvalidKeyname)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
