#!/usr/bin/python
#
#  File name: add_remove_mult_ssh_keys.py
#  Date:      2012/03/20 10:52
#  Author:    mzimen@redhat.com
#

import os

import testcase, common
import rhtest
# user defined packages

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.key_name1 = common.getRandomString(10)
        self.key_name2 = common.getRandomString(10)
        self.key_file_name1 = common.getRandomString(10)
        self.key_file_name2 = common.getRandomString(10)
        tcms_testcase_id = 141794
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -f %s"%self.key_file_name1)
        os.system("rm -f %s"%self.key_file_name2)
        common.remove_sshkey(self.key_name1)
        common.remove_sshkey(self.key_name2)


class AddRemoveMultSshKeys(OpenShiftTest): 
    def test_method(self):
        status1 = common.command_get_status("ssh-keygen -t rsa -N '' -f %s" % self.key_file_name1)
        status2 = common.command_get_status("ssh-keygen -t rsa -N '' -f %s" % self.key_file_name2)
        
        if status1 != 0 or status2 != 0:
            return self.failed("Unable to create a ssh key")

        self.steps_list.append(testcase.TestCaseStep("Add created key as %s"%self.key_name1,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_file_name1), self.key_name1, self.user_email, self.user_passwd],
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Add created key as %s"%self.key_name2,
                                  common.add_sshkey,
                                  function_parameters=["%s.pub" % (self.key_file_name2), self.key_name2, self.user_email, self.user_passwd],
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Remove the first one" ,
                                  common.remove_sshkey,
                                  function_parameters=[self.key_name2, self.user_email, self.user_passwd],
                                  expect_return=0,
                                  expect_description="Should remove only one the %s not the %s (despite they are the same)"%(self.key_name2, self.key_name1)))

        self.steps_list.append(testcase.TestCaseStep("Check the %s"%self.key_name1,
                                  "rhc sshkey list -l %s -p '%s' %s"%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_string_list=["%s"%self.key_name1],
                                  unexpect_string_list=["%s"%self.key_name2],
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Remove the second one",
                                  common.remove_sshkey,
                                  function_parameters=[self.key_name1, self.user_email, self.user_passwd],
                                  expect_return=0,
                                  expect_description="Should remove the %s"%self.key_name1))

        self.steps_list.append(testcase.TestCaseStep("Check both keys - %s/%s"%(self.key_name1, self.key_name2),
                                  "rhc sshkey list -l %s -p '%s' %s"%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  unexpect_string_list=["%s"%self.key_name1, "%s"%self.key_name2],
                                  expect_return=0))

        case = testcase.TestCase("Add/remove multi ssh keys with same value and different names",
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
    suite.add_test(AddRemoveMultSshKeys)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
                   

#
# end of add_remove_mult_ssh_keys.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
