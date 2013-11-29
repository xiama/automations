#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

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
	self.test_variant=self.config.test_variant
        self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
	self.domain_name = common.get_domain_name()
        self.app_type = common.app_types[self.test_variant]
        self.app_name = 'my%s%s' % ( self.test_variant, common.getRandomString() )
        self.git_repo = './' + self.app_name
        try:
            os.putenv('https_proxy', os.environ['http_proxy'])
        except:
            pass
    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class ManualScaling(OpenShiftTest):
    def configure_scale_up_test_application(git_repo):
        new_file = open(git_repo + "/php/gear.php", "w")
        new_file.write("<?php\n")
        new_file.write("header(\"Content-Type: text/plain\");\n")
        new_file.write("echo $_ENV[\"OPENSHIFT_GEAR_DNS\"];\n")
        new_file.write("?>")
        new_file.close()

        configuration_steps = [
            "cd %s" % ( git_repo ),
            "git add php",
            "git commit -a -m gear.php",
            "git push"
        ]

        return common.command_get_status(" && ".join(configuration_steps))

    def number_of_gears(app_name):
        app_url = OSConf.get_app_url(app_name)
        gears = list()

        # Checking the output of gear dns script more times
        for i in range(1, 11):
            gear = common.fetch_page(app_url + "/gear.php")
            if gear not in gears:
                gears.append(gear)

        return len(gears)

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Creating a scalable application",
            common.create_app,
            function_parameters = [ self.app_name, self.app_type, self.user_email, self.user_passwd, True, self.git_repo, True ],
            expect_description = "The application must be created successfully",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scaling up via REST API",
            common.scale_up,
            function_parameters = [ self.domain_name, self.app_name ],
            expect_description = "The application must scale-up successfully",
            expect_return = 0,
        ))

        # Checking web-page availability with refreshing
        for i in range(1,6):
            self.steps_list.append(testcase.TestCaseStep(
                "Checking web-page #%d" % ( i ),
                common.check_web_page_output,
                function_parameters = [ self.app_name ],
                expect_description = "The application must be available in the browser",
                expect_return = 0
            ))

        self.steps_list.append(testcase.TestCaseStep(
            "Configuring the test application",
            self.configure_scale_up_test_application,
            function_parameters = [ self.git_repo ],
            expect_description = "The application must be configured successfully",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Checking the number of gears",
            self.number_of_gears,
            function_parameters = [ self.app_name ],
            expect_description = "The number of gears must be '2'",
            expect_return = 2
        ))
        case = testcase.TestCase("[US1463][BusinessIntegration] Scale-up / Scale down an application ", self.steps_list)
        case.add_clean_up(
        "rm -Rf %s" % ( self.git_repo )
        )
        case.run()

	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ManualScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
