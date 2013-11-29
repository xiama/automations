#!/usr/bin/env python

"""
"""
import rhtest
import database
import time
import testcase
import common
import OSConf
import random

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "SmokeTest"
        self.info("SmokeTest")
        self.test_variant = "php"
        self.info("VARIANT: %s"%self.test_variant)
        self.scalable = True 
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = './' + self.app_name
        self.steps_list = []

        params = {'klass': self, 'mode': 1, 'app_type': 'php'}
        self = common.setup_testbed(**params)

    def finalize(self):
        pass


class SmokeTest(OpenShiftTest):
    def test_method(self):
        # step 1: add scalable php app
        self.steps_list.append(testcase.TestCaseStep(
                'Creating a scalable application',
                common.create_app,
                function_parameters = [
                    self.app_name,
                    self.app_type, 
                    self.config.OPENSHIFT_user_email, 
                    self.config.OPENSHIFT_user_passwd, 
                    True, self.git_repo, self.scalable],
                    expect_description = 'The app should be created successfully',
                    expect_return = 0))
        # step 2: add mysql to app
        self.steps_list.append(testcase.TestCaseStep(
                'Embedding MySQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['mysql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'MySQL cartridge should be embedded successfully',
                expect_return = 0))
        errorCount = 0


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
    suite.add_test(SmokeTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
