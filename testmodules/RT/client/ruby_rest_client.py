#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

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

    def initialize(self):
        self.user_email = os.environ["OPENSHIFT_user_email"]
        self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.domain_name = common.get_domain_name()
        self.libra_server = common.get_instance_ip()

        tcms_testcase_id=135780

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass

def rhc_rest_client_configuration():

    # Most of the operations require to be root
    if os.geteuid() != 0:
        print "You have to run this script as root"
        return 1

    configuration_steps = [
        "if [[ $(ruby -e 'require \"rubygems\" ; puts Gem.available?(\"rhc-rest\")') == 'true' ]]; then gem uninstall rhc-rest -x ; fi", # Cleaning
        "cd /tmp",
        "if [[ -e os-client-tools ]]; then rm -Rfv os-client-tools/ ; fi", # Cleaning
        "git clone git://github.com/openshift/os-client-tools.git",
        "cd os-client-tools/rhc-rest/",
        "gem build rhc-rest.gemspec",
        "gem install rhc-rest"
    ]

    ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(configuration_steps))
    return ret_code


class RubyRestClient(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep(
            "Configuring RHC REST client",
            rhc_rest_client_configuration,
            function_parameters = [ ],
            expect_description = "The RHC REST client library must be installed successfully",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Testin Rhc::Rest::Client",
            "%s/rhc_rest_client_test.rb https://%s/broker/rest %s %s %s" % ( WORK_DIR, self.libra_server, self.user_email, self.user_passwd, self.domain_name ),
            expect_description = "Ruby RHC client library script should be executed without any errors",
            expect_return = 0
        ))

        case = testcase.TestCase("[US1841][BusinessIntegration][Mirage] Ruby rest common client library", self.steps_list )
        case.add_clean_up(common.alter_domain, [self.domain_name])
        case.run()
	
	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RubyRestClient)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
