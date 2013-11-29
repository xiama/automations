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
        self.key_filename = "/tmp/libra_id_rsa1-%s"%(os.getpid())
        tcms_testcase_id = 131033
        common.env_setup()
        self.key_name = common.getRandomString(10)
        self.steps_list = []

    def finalize(self):
        common.update_sshkey()
        os.system("rm -rf %s"%self.key_filename)


class RhcWrapperSsh(OpenShiftTest):
    def test_method(self):
        step = testcase.TestCaseStep("Create additional key" ,
                                  "ssh-keygen -f %s -N '' "%self.key_filename,
                                  expect_return=0)
        self.steps_list.append(step)

        
        step = testcase.TestCaseStep("rhc help sshkey" ,
                                  "rhc help sshkey",
                                  expect_return=0,
                                  expect_string_list=["list", "add", "remove"])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc sshkey add...",
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % self.key_filename, self.key_name, self.user_email, self.user_passwd],
                                  expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("rhc sshkey list...",
                                  "rhc sshkey list -l %s -p %s %s"%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0,)
        self.steps_list.append(step)


        step = testcase.TestCaseStep("rhc sshkey remove...",
                                  common.remove_sshkey,
                                  function_parameters=[self.key_name, self.user_email, self.user_passwd],
                                  expect_return=0)
        self.steps_list.append(step)
        '''
        step = testcase.TestCaseStep("Copy new keys to correct place" ,
                                  "cp %s.pub $HOME/.ssh/id_rsa.pub && cp %s $HOME/.ssh/id_rsa" %(self.key_filename, self.key_filename),
                                  expect_return=0)
        self.steps_list.append(step)
        '''


        case = testcase.TestCase("[US1317][UI][CLI]rhc wrapper - rhc sshkey", steps=self.steps_list)
        case.run()
    
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcWrapperSsh)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
