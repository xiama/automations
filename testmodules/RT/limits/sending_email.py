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
        self.app_type = "python"
        self.app_name = 'my%s%s' % ( self.app_type, common.getRandomString() )
        self.git_repo = './' + self.app_name
        tcms_testcase_id=126091

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass

class SendingEmail(OpenShiftTest):
    def app_config(self, git_repo, work_dir):
        configuration_steps = [
            "cd %s" % ( git_repo ),
            "cp -fv %s/app_template/sending_email/application wsgi/application" % ( work_dir ),
            "git commit -a -m deployment",
            "git push"
        ]

        ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(configuration_steps))
        print ret_output
        return ret_code

    def check_port_result(self, app_name, path, pattern):
        app_url = OSConf.get_app_url(app_name)
        return common.grep_web_page("http://%s/%s" % ( app_url, path ) , pattern )
 
    def test_method(self):

	self.steps_list.append(testcase.TestCaseStep(
            'Creating the application',
            common.create_app,
            function_parameters = [ self.app_name,common.app_types[self.app_type], self.user_email, self.user_passwd, True, self.git_repo ],
            expect_description = 'The app should be created successfully',
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            'Configuring our Python application',
            self.app_config,
            function_parameters = [ self.git_repo, WORK_DIR ],
            expect_description = 'App configuration should be successful',
            expect_return = 0
        ))

        for protocol in [ 'Submission', 'SMTP', 'SSMTP' ]:
            self.steps_list.append(testcase.TestCaseStep(
                'Checking %s port' % ( protocol ),
                self.check_port_result,
                function_parameters = [ self.app_name, protocol.lower(), protocol.upper() + " SUCCESS" ],
                expect_description = "The application should access Google's %s port" % ( protocol ),
                expect_return = 0
            ))
        step=testcase.TestCaseStep(
            "Destroy app: %s" % (self.app_name),
            common.destroy_app,
            function_parameters = [self.app_name],
            expect_return = 0)
        self.steps_list.append(step)


        case= testcase.TestCase("[Runtime][rhc-cartridge] Sending E-mail", self.steps_list )
        case.run()
                      
	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SendingEmail)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
