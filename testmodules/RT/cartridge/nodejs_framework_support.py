#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Feb 14, 2012

[US590][Runtime][rhc-cartridge]nodejs framework support
https://tcms.engineering.redhat.com/case/136576/
"""

import os
import sys
import shutil
import re
import fileinput

import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US590][Runtime][rhc-cartridge]nodejs framework support"
        self.app_type = 'nodejs'
        self.app_name = 'my%s%s' % ( self.app_type, common.getRandomString() )
        self.git_repo = './' + self.app_name
        self.steps_list = []
        self.random_string = common.getRandomString()

        common.env_setup()

    def finalize(self):
        pass

class NodeJsFrameworkSupport(OpenShiftTest):

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
                'Creating the application',
                common.create_app,
                function_parameters = [ self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, ],
                expect_description = 'The app should be created successfully',
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                'Checking welcome screen',
                common.check_web_page_output,
                function_parameters = [ self.app_name ],
                expect_description = 'The index page must be OpenShift branded',
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                'Configuring the application',
                self.configuring_nodejs_app,
                function_parameters = [ self.git_repo, self.random_string ],
                expect_description = "Condiguration of our NodeJS should be successfull",
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
                'Checking NodeJS web-page output',
                common.check_web_page_output,
                function_parameters = [ self.app_name, '', self.random_string ],
                expect_description = 'In output we have to find our random string',
                expect_return = 0))
    
        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def configuring_nodejs_app(self, git_repo, random_string):

        try:
            file_name = git_repo + "/server.js"
            for line in fileinput.input(file_name, inplace = True):
                match = re.search(r"res.send\(self.cache_get\('index.html.*", line)
                if match:
                    print 'res.send("<html><head></head><body><p>%s</p></body></html>");' % ( random_string )
                else:
                    print line,
        except Exception as e:
            fileinput.close()
            print type(e)
            print e.args
            return 1
        finally:
            fileinput.close()

        deployment_steps = [
            "cd %s" % ( git_repo ),
            "git commit -a -m 'Added special handler for /'",
            "git push" ]

        ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(deployment_steps))
        print ret_output
        return ret_code


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NodeJsFrameworkSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
