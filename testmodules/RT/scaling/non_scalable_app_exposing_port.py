#!/usr/bin/env python
import os, sys

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = 'DEV'

    def initialize(self):
        self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.domain_name = common.get_domain_name()
        self.test_variant=self.config.test_variant
        self.app_type = common.app_types[self.test_variant]
        self.app_name = 'my%s%s' % ( self.test_variant, common.getRandomString() )
        tcms_testcase_id = 138428
        self.rest_client = openshift.Openshift(host=self.config.instance_info['ip'],
                           user=self.user_email,
                           passwd=self.user_passwd)

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass


class NonScalableAppExposingPort(OpenShiftTest):
    def existing_exposed_ports(self):
  
        (gears, number_of_gears) = self.rest_client.get_gears(self.app_name, self.domain_name)

        exposed_ports = 0
        for component in gears[0]['components']:
            if component['proxy_port'] != None and component['proxy_host'] != None:
                exposed_ports += 1

        return exposed_ports

    def exposing_port(self, cartridge):
        return common.run_remote_cmd_as_root(
            "/usr/libexec/openshift/cartridges/embedded/%s/info/hooks/expose-port %s %s %s" %
            (
                cartridge,
                self.app_name,
                self.domain_name,
                OSConf.get_app_uuid(self.app_name)
            )
        )[0]

    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep(
            "Creating an application",
             common.create_app,
             function_parameters = [ self.app_name, self.app_type, self.user_email, self.user_passwd, False ],
             expect_description = "The application must be created successfully",
             expect_return = 0
       ))

        self.steps_list.append(testcase.TestCaseStep(
            "Embedding MySQL cartridge",
            common.embed,
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"] ],
            expect_description = "MySQL cartridge must be embedded successfully",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Verifying the number of exposed ports",
            self.existing_exposed_ports,
            expect_description = "The number of exposed ports must be 0",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Expose port information",
            self.exposing_port,
            function_parameters = [ common.cartridge_types['mysql'] ],
            expect_description = "The operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Verifying the number of exposed ports after the manual exposion",
            self.existing_exposed_ports,
            expect_description = "The number of exposed ports must be 1",
            expect_return = 1
        ))

        case = testcase.TestCase("[US1907][BusinessIntegration] Retrive gear information by explicitly exposing port for a non-scalable app", self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NonScalableAppExposingPort)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
