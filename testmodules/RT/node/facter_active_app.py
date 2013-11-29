
#
#  File name: facter_active_app.py
#  Date:      2012/02/24 05:04
#  Author:    mzimen@redhat.com
#

import sys
import os
import re

import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    ITEST = 'DEV'

    def initialize(self):
        self.summary = "[rhc-node] [US1734] New metric for facter reporting about the active applications on the current node"
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'
        tcms_testcase_id = 130874
        self.steps= []
        if self.get_run_mode() == "OnPremise":
            self.origin_max_apps = 1000
        else:
            self.origin_max_apps = 80

        common.env_setup()


    def finalize(self):
        common.run_remote_cmd(None,"sed -i s'/max_active_apps=.*/max_active_apps=%d/' /etc/openshift/resource_limits.conf" % (self.origin_max_apps), True)

class FacterActiveApp(OpenShiftTest):
    def test_method(self):
        max_apps = 3
        destroy_apps = int(max_apps/2)
        #1) In the file '/etc/openshift/resource_limits.conf' change the value 'max_apps' to <max_apps>, change the value 'max_active_apps' to <max_apps>
        #common.run_remote_cmd(None,"sed -i s'/max_apps=.*/max_apps=%d/' /etc/openshift/resource_limits.conf" % (max_apps), as_root=True)
        #common.run_remote_cmd(None,"sed -i s'/max_active_apps=.*/max_active_apps=%d/' /etc/openshift/resource_limits.conf" % (max_apps), as_root=True)
        self.steps.append(testcase.TestCaseStep("Change the value of max_apps",
                common.run_remote_cmd,
                function_parameters = [None,"sed -i s'/max_active_apps=.*/max_active_apps=%d/' /etc/openshift/resource_limits.conf" % (max_apps), True]))

        #2) Create <max_apps> applications
        for i in range(max_apps):
            self.steps.append(testcase.TestCaseStep("Create app#%d"%i ,
                    common.create_app,
                    function_parameters=[self.app_name+"%d"%i, 
                                         common.app_types[self.app_type], 
                                         self.user_email, 
                                         self.user_passwd, False],
                    expect_return=0))

        def verify_facter(percent):
            (status, output) = common.run_remote_cmd(None, 'facter active_capacity', True)
            if status!=0:
                return 1
            obj = re.search(r"^%s"%percent, output)
            if obj:
                return 0
            return 1

        self.steps.append(testcase.TestCaseStep("Verify the facter active_capacity" ,
                verify_facter,
                function_parameters=[100],
                expect_description = "Should be active_capacity => 100%",
                expect_return=0))
        #3) Destroy <destroy_apps> application
        for i in range(destroy_apps):
            self.steps.append(testcase.TestCaseStep("Destroy app#%d"%i ,
                    common.destroy_app,
                    function_parameters=[self.app_name+"%d"%i, 
                                         self.user_email, 
                                         self.user_passwd, True],
                    expect_return=0))

        expect_capacity = int(float(max_apps - destroy_apps) / (max_apps) * 100)
        self.steps.append(testcase.TestCaseStep("Verify the facter active_capacity" ,
                verify_facter,
                function_parameters=[expect_capacity],
                expect_description = "Should be capacity => %d%%" % (expect_capacity),
                expect_return=0))

        #4) Create <destroy_apps> new applications
        for i in range(destroy_apps):
            self.steps.append(testcase.TestCaseStep("Create app#%d"%i ,
                    common.create_app,
                    function_parameters=[self.app_name+"%d"%i, 
                                         common.app_types[self.app_type], 
                                         self.user_email, 
                                         self.user_passwd, False],
                    expect_return=0,
                    try_count=3,
                    try_interval=20))

        #5) Create an additional application
        self.steps.append(testcase.TestCaseStep("Create over limit app",
                common.create_app,
                function_parameters = [self.app_name+"OVER", 
                                       common.app_types[self.app_type], 
                                       self.user_email, 
                                       self.user_passwd, False],
                expect_string_list = ["No nodes available",], 
                expect_return="!0"))

        case = testcase.TestCase(self.summary, self.steps)
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
    suite.add_test(FacterActiveApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of facter_active_app.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
