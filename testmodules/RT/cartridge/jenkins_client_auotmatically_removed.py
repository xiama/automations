#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Feb 14, 2012

[Runtime]Embedded jenkins client should be removed automatically after remove jenkins app
https://tcms.engineering.redhat.com/case/136548/
"""

import os
import sys
import shutil
import commands
import re

import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[Runtime]Embedded jenkins client should be removed automatically after remove jenkins app"
        try:
            test_name = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, using `python` as default")
            test_name = 'python'

        self.app_type = common.app_types[test_name]
        self.app_name1 = 'my%s%s' % ( test_name, common.getRandomString() )
        self.app_name2 = 'my%s%s' % ( test_name, common.getRandomString() )
        self.steps= []
        self.jenkins_name = "jenkins"

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name1, self.app_name2))
        common.destroy_app(self.jenkins_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True)

class JenkinsClientAutomaticallyRemoved(OpenShiftTest):
    def check_jenkins_client(self, app_name):
        (ret, output) = common.command_getstatusoutput("rhc app show %s -l %s -p '%s' %s" % (app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        if ret != 0:
            return False
        if re.search(r'jenkins-client', output) == None:
            return True
        else:
            return False

    def test_method(self):
        self.steps.append(testcase.TestCaseStep(
                'Creating Jenkins app',
                common.create_app,
                function_parameters = [ self.jenkins_name, common.app_types['jenkins'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False ],
                expect_description = 'Jenkins app should be created successfully',
                expect_return = 0))

        for a in [ self.app_name1, self.app_name2 ]:
            self.steps.append(testcase.TestCaseStep(
                    'Creating application: %s' % ( a ),
                    common.create_app,
                    function_parameters=[a, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False ],
                    expect_description = 'The app should be created successfully',
                    expect_return = 0))

        for a in [ self.app_name1, self.app_name2 ]:
            self.steps.append(testcase.TestCaseStep(
                'Embedding Jenkins client to the application %s' % ( a ),
                common.embed,
                function_parameters = [ a, 'add-%s' % ( common.cartridge_types['jenkins'] ), self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd ],
                expect_description = 'Jenkins client cartridge should be embedded successfully',
                expect_return = 0,
                try_count=3,
                try_interval=5))

        self.steps.append(testcase.TestCaseStep(
                'Deleting Jenkins app',
                "rhc app delete %s -l %s -p '%s' --confirm %s" 
                    % (self.jenkins_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description = 'Jenkins app should be destroyed + jenkins client cartridge should be removed from applications',
                expect_return = 0))

        for app_name in [self.app_name1, self.app_name2]:
            self.steps.append(testcase.TestCaseStep(
                "Check if jenkins client has been removed from app: %s" % (app_name),
                self.check_jenkins_client,
                function_parameters = [app_name,],
                expect_description = "Jenkins client shouldn't exist in the cartridges of app",
                expect_return = True))


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
    suite.add_test(JenkinsClientAutomaticallyRemoved)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
