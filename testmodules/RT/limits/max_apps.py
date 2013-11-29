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
import re

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = 'DEV'

    def initialize(self):
        self.user_email = os.environ["OPENSHIFT_user_email"]
        self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_type = "python"
        self.max_apps = 7
        self.app_name = 'my%s%s' % ( self.app_type, common.getRandomString() )
        self.git_repo = './' + self.app_name
        tcms_testcase_id=130893
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass


class MaxApps(OpenShiftTest):
    def max_apps_config(self, git_repo, work_dir, max_apps, user_email):
        configuration_steps = [
            "cd %s" % ( git_repo ),
            "cp -fv %s/app_template/max_gears/application wsgi/application" % ( work_dir ),
            "sed -i -e 's/#mongodb_max_gears#/%s/;s/#mongodb_user_email#/%s/' wsgi/application" % ( max_apps, user_email ),
            "git commit -a -m deployment",
            "git push"
        ]

        ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(configuration_steps))
        print ret_output
        return ret_code

    def check_mongodb_operation_result(self, app_name):
        app_url = OSConf.get_app_url(app_name)
        return common.grep_web_page("http://%s/%s" % ( app_url, "set-max-gears"), "DB OPERATION SUCCESS" )


    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            'Creating the first application',
            common.create_app,
            function_parameters = [ self.app_name, common.app_types[self.app_type], self.user_email, self.user_passwd, True, self.git_repo ],
            expect_description = 'The app should be created successfully',
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            'Configuring out Python application',
            self.max_apps_config,
            function_parameters = [ self.git_repo, WORK_DIR, self.max_apps, self.user_email ],
            expect_description = 'The MongoDB configuration should be successful',
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            'MongoDB - setting "max_gears" property',
            self.check_mongodb_operation_result,
            function_parameters = [ self.app_name ],
            expect_description = 'MongoDB operation must be successful',
            expect_return = 0
        ))

        for i in range(2, self.max_apps + 1):
            self.steps_list.append(testcase.TestCaseStep(
                'Creating application #%d' % ( i ),
                common.create_app,
                function_parameters = [ self.app_name + str(i), common.app_types[self.app_type], self.user_email, self.user_passwd, False, self.git_repo + str(i) ],
                expect_description = "Creation of application #%d should be successful" % ( i ),
                expect_return = 0
            ))

        step=testcase.TestCaseStep(
            'Creation of application N+1',
            common.create_app,
            function_parameters =  [ self.app_name + 'last', common.app_types[self.app_type], self.user_email, self.user_passwd, False, self.git_repo + 'last' ],
            expect_description = 'Creation of the last application should be NOT successful',
            expect_return = "!0"
        )
        step.add_clean_up(common.destroy_app, [self.app_name, self.user_email, self.user_passwd])
        self.steps_list.append(step)

        case = testcase.TestCase("[rhc-node] [US1733] Allotment: Max Apps", self.steps_list )
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MaxApps)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
