#!/usr/bin/env python

"""
demo test script for running variants

"""
import rhtest
import database
import time
import os

#from lib import testcase, common, OSConf
import openshift
import common
import testcase

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.rest = self.config.rest
        common.env_setup()

def finalize(self):
        pass


class Demo02(OpenShiftTest):
    def test_method(self):

        for variant in self.config.test_variants['variants']:
            self.app_type = common.app_types[variant]
            #
            status, res = self.rest.app_create(self.app_name, self.app_type)


        return self.failed("test failed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo02)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
