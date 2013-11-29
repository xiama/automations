#!/usr/bin/env python
import os, sys

"""
Attila Nagy
anagy@redhat.com
May 9, 2012

[US1876] App creation should fail without domain
"""

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift
import re

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_name = common.getRandomString(10)
        self.current_domain = common.get_domain_name()
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        common.create_domain(common.getRandomString(10), self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)

class AppCreationWithoutDomain(OpenShiftTest):
    def test_method(self):

        if self.current_domain is not None and self.current_domain != '':
            try:
                common.command_get_status("rhc domain delete %s -l %s -p '%s' %s" % ( self.current_domain, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
            except:
                return self.failed("Unable to destroy domain.")
        else:
            self.info("Domain doesn't exist, no need to destroy it.")

        self.steps_list.append(testcase.TestCaseStep(
            "Trying to create an application without an existing domain",
            common.create_app,
            function_parameters = [ self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False ],
            expect_description = "Operation must fail",
            expect_return = "!0"
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Creating a domain name",
            common.create_domain,
            function_parameters = [ common.getRandomString(10), self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd ],
            expect_description = "Domain must be created successfully",
            expect_return = 0,
            expect_string_list = [ "You may now create an application" ]
        ))
        
        self.steps_list.append(testcase.TestCaseStep(
            "Creating an application",
            common.create_app,
            function_parameters = [ self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False ],
            expect_description = "The application must be created successfully",
            expect_return = 0
        ))

        case=testcase.TestCase("[US1876] App creation should fail without domain",self.steps_list)
        case.run()
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppCreationWithoutDomain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
