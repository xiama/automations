#
#  File name: ssh_selinux_transition.py
#  Date:      2012/02/13 10:07
#  Author:    mzimen@redhat.com
#

import sys
import os
import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary ="[US1657][Runtime][rhc-cartridge] SSH Transition protection"
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'

        self.app_name = 'selinuxapp'
        self.tcms_testcase_id = 130919

        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class SshSelinuxTransisition(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create sample application",
                common.create_app,
                function_parameters=[self.app_name, 
                                     common.app_types[self.app_type], 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        pexpect_cmd = [
            ('sendline', 'ps -efwwZ |grep grep'),
            ('expect', 'unconfined_u:system_r:openshift_t:.*grep grep')
        ]

        self.steps_list.append(testcase.TestCaseStep("Login through RHCSH and check the SELinux label",
                common.rhcsh,
                function_parameters = [self.app_name, pexpect_cmd],
                expect_return = 0,
                expect_description="Tenants' sshd process should be labled as openshift_t instead of ssh_t."))


        case = testcase.TestCase(self.summary, self.steps_list)
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
    suite.add_test(SshSelinuxTransisition)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of  ssh_selinux_transition.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
