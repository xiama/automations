#!/usr/bin/python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]Verify git push works well if stop app before git push
https://tcms.engineering.redhat.com/case/122289/
"""

import sys,os,commands,time,re
import rhtest
import testcase,common,OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge]Verify git push works well if stop app before git push"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.test_variant =  'php'

        self.app_name = self.test_variant.split('-')[0] + 'uponstop'
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        tcms_testcase_id=122289
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass

class GitPushUponAppStopped(OpenShiftTest):

    def test_method(self):

        # 1.Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # Clean environment variable: SSH_AUTH_SOCK
        if os.environ.has_key("SSH_AUTH_SOCK"):
            del os.environ["SSH_AUTH_SOCK"]

        # 2.Stop Application
        self.steps_list.append( testcase.TestCaseStep("2. Stop Application",
                "rhc app stop %s -l %s -p '%s' %s" 
                    % (self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="App is stopped successfully",
                expect_return=0))
        # 3.Check the app is unavailable via browser
        
        self.steps_list.append( testcase.TestCaseStep("3.Check the app is unavailable via browser",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), "Service Temporarily Unavailable", "-H 'Pragma: no-cache'", 3, 6],
                expect_description="The app is unavailable",
                expect_return=0))

        # 4.Custom git hook file
        hook_file_path = "%s/.openshift/action_hooks/build" % (self.app_name)
        key_string = "@@@testing@@@"
        self.steps_list.append( testcase.TestCaseStep("4.Custom git hook file",
                """echo '\necho "%s"' >> %s && chmod +x %s""" % (key_string, hook_file_path, hook_file_path),
                expect_description="Added 1 line to %s" % (hook_file_path),
                expect_return=0))

        # 5.Git push
        self.steps_list.append( testcase.TestCaseStep("5.Git push all the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="Git push succeeds and '%s' should be found in the output" % (key_string),
                expect_return=0,
                expect_string_list=[key_string]))

        # 6.Check to see if the app is available
        test_html = "Welcome to OpenShift"
        self.steps_list.append( testcase.TestCaseStep(
                "6.Check to see if the app is available",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 5, 8],
                expect_description="'%s' should be found in the web page" % (test_html),
                expect_return=0))

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
    suite.add_test(GitPushUponAppStopped)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
