#!/usr/bin/env python
import os, sys

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
#import openshift


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        tcms_testcase_id=141682
        params = {'klass': self, 'mode': 2, 'app_type': 'php'}
        self = common.setup_testbed(**params)

        #status, res = rest.app_create(self.app_name, self.app_type)

    def finalize(self):
        pass


class RestApiAlias(OpenShiftTest):
    def test_method(self):
        cf = self.config
        rest = cf.rest_api
        alias_name = "my_other_name"
        invalid_alias_name = "[]"
        self.info("Adding alias to existing app using REST API...")
        status, res = rest.app_add_alias(cf.app_name, alias_name)
        self.info("OP STATUS: %s"  % status)
        status, res = rest.app_remove_alias(cf.app_name, alias_name)
        self.info("OP STATUS: %s"  % status)
        status, res = rest.app_add_alias(cf.app_name,  invalid_alias_name)
        self.info("OP STATUS: %s"  % status)

        #cf.rest_api.app_add_alias(
        if status == 'Unprocessable Entity':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RestApiAlias)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
