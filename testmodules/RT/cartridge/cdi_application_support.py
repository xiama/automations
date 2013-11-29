"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US504][rhc-cartridge]JBoss cartridge: CDI application support
https://tcms.engineering.redhat.com/case/122406/
"""
import sys, os, re, time, random

import testcase
import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US504][rhc-cartridge]JBoss cartridge: CDI application support"

        self.app_name = "weldguess"
        self.git_repo = "./%s" % self.app_name
        self.app_type = common.app_types["jbossas"]
        tcms_testcase_id=122406
        common.env_setup()

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s* "%(self.app_name))

class CdiApplicationSupport(OpenShiftTest):

    def test_method(self):
        # 1.Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an jbossas app",
                common.create_app,
                function_parameters=[self.app_name,self.app_type,self.config.OPENSHIFT_user_email,self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Copy weldguess.war to <app_repo>/deployments
        self.steps_list.append(testcase.TestCaseStep("2.Copy weldguess.war to /tmp/reponame/deployments",
                "cp %s/app_template/weldguess.war %s/deployments && cd %s/deployments && touch weldguess.war.dodeploy" % (WORK_DIR, self.git_repo, self.git_repo),
                expect_description="Copy succeed",
                expect_return=0))

        # 3.Git push all the changes
        self.steps_list.append(testcase.TestCaseStep("3.Git push all the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="Git push should succeed",
                expect_return=0))

        # 4.Check app via browser
        def get_app_url(app_name):
            def closure():
                return OSConf.get_app_url(app_name) + "/weldguess/home.jsf"
            return closure

        self.steps_list.append(testcase.TestCaseStep("4. Access the app's URL",
                common.grep_web_page,
                function_parameters=[get_app_url(self.app_name), "Guess a number", "-H 'Pragma: no-cache'", 3, 6],
                expect_description="'Guess a number' should be found in the web page",
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
    suite.add_test(CdiApplicationSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
