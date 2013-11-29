#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Feb 23, 2012

[US1107][rhc-cartridge] App git repo cleanup using git gc
https://tcms.engineering.redhat.com/case/122511/
"""

import os
import sys
import re

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):

        self.summary = "[US1107][rhc-cartridge] App git repo cleanup using git gc"
        test_name = "python"
        self.app_type = common.app_types[test_name]
        self.app_name = 'my%s%s' % ( test_name, common.getRandomString() )
        self.git_repo = './' + self.app_name
        self.steps = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class GitRepoCleanupGc(OpenShiftTest):
    def test_method(self):
        self.steps.append(testcase.TestCaseStep(
                'Creating an application',
                common.create_app,
                function_parameters = [ self.app_name, 
                                        self.app_type, 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd, 
                                        False, self.git_repo ],
                expect_description = 'The app should be created successfully',
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                "Performing 'git gc' and comparing git repo sizes",
                self.comparing_git_repo_size,
                expect_description = "The new size of the git repo must be less than it was before 'git gc'",
                expect_return = 1)) # It's a Python function, so it returns 1 if the comparation was successfull


        case = testcase.TestCase(self.summary, self.steps)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def comparing_git_repo_size(self):
        """
        This functions returns 1 if the comperation was successfull ( new_size < original_size)
        Returns 0 otherwise
        """
        try:
            original_size = common.get_git_repo_size(self.app_name)
        except Exception as e:
            raise rhtest.TestIncompleteError(str(e))

        ( gc_rc, gc_output ) = common.run_remote_cmd(self.app_name, r"cd git/%s.git && git gc" % ( self.app_name ))
        if gc_rc != 0:
            print "Failed to execute 'git gc'"
            return 0

        try:
            new_size = common.get_git_repo_size(self.app_name)
        except Exception as e:
            raise rhtest.TestIncompleteError(str(e))

        if int(new_size) < int(original_size):
            return 1
        else:
            return 0


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(GitRepoCleanupGc)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
