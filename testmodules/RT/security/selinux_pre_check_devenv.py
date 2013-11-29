"""
Linqing Lu
lilu@redhat.com
Dec 23, 2011

"""

import os, sys

import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary="[integration][rhc-selinux]SELinux separation - devenv pre check"
        self.info(self.summary)
        common.env_setup()

class SELinuxPreCheck(OpenShiftTest):
    def test_method(self):
        self.info("check_selinux_status")
        (ret, output) = common.run_remote_cmd_as_root("sestatus")
        self.assert_match(['SELinux status:.*enabled', 'Current mode:.*enforcing', 'Mode from config file:.*enforcing'], output)
        self.assert_equal(ret, 0)

        self.info("Get semodule list")
        (ret, output) = common.run_remote_cmd_as_root("semodule -l|grep libra")
        self.assert_match('libra', output)
        self.assert_equal(ret, 0)

        self.info("Check audit service")
        (ret, output) = common.run_remote_cmd_as_root("service auditd status")
        self.assert_equal(ret, 0)
        self.assert_match(['auditd .* is running...'], output)


        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SELinuxPreCheck)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
