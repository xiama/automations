#!/usr/bin/env python

import os
import common
import OSConf
import rhtest
import random


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        valid_variants = ["jbossas", "jbosseap", "php", "ruby", "ruby-1.9", "python", "wsgi", "perl", "diy", "nodejs"]
        random.seed()
        rand = int(random.random() * len(valid_variants))
        self.app_type = common.app_types[valid_variants[rand]]

        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.domain_name = common.get_domain_name(self.user_email, self.user_passwd)
        self.new_domain_name = common.getRandomString(10)
        self.app_name = "testapp%s"%(common.getRandomString(4))
        common.env_setup()

    def finalize(self):
        common.alter_domain(self.domain_name, self.user_email, self.user_passwd)


class AlterNamespace(OpenShiftTest):
    def test_method(self):

        self.info("Alter namespace test.")

        self.add_step("Create app",
                      common.create_app,
                      function_parameters=[self.app_name, 
                                           self.app_type, 
                                           self.user_email, 
                                           self.user_passwd, 
                                           False],
                      expect_return=0)

        self.add_step("Change domain namespace to new one",
                      common.alter_domain,
                      function_parameters=[self.new_domain_name, self.user_email, self.user_passwd],
                      expect_return=0)

        self.add_step("Get app url",
                      OSConf.get_app_url,
                      function_parameters = [self.app_name])

        self.add_step("Get app git repo url",
                      OSConf.get_git_url,
                      function_parameters = [self.app_name])

        self.add_step("Check new app url is available",
                      common.grep_web_page,
                      function_parameters = ["__OUTPUT__[3]", "Welcome to OpenShift"],
                      expect_return=0)

        self.add_step("Check new app git repo is available",
                      "git clone __OUTPUT__[4]",
                      expect_return=0)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AlterNamespace)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
