#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]PHP sqlite Support
https://tcms.engineering.redhat.com/case/122284/
"""
import os,sys,re,time

import testcase,common,OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge]PHP sqlite Support"
        self.app_name = "phpsqlite"
        self.app_type = common.app_types["php"]
        self.git_repo = "./%s" % (self.app_name)
        tcms_testcase_id=122284
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class PhpSqliteSupport(OpenShiftTest):

    def test_method(self):
        # 1.Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an php app: %s" % (self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Make some change to the git repo
        cmd = "cd %s/php && mkdir db && touch db/test && rm -f index.php" % (self.git_repo)
        self.steps_list.append(testcase.TestCaseStep("2.Make some change to the git repo",
                cmd,
                expect_description="Successfully touched test and removed index.php",
                expect_return=0))

        # 3.Copy app template to the git repo and git push
        cmd = "cp %s/app_template/php-sqlite.template %s/php/index.php && cd %s && git add . && git commit -am t && git push" %(WORK_DIR, self.git_repo, self.git_repo)
        self.steps_list.append(testcase.TestCaseStep("3.Copy app template to the git repo and git push",
                cmd,
                expect_description="Copy and git push succeed",
                expect_return=0))

        # 4.Check app via browser
        test_html = "done"
        self.steps_list.append(testcase.TestCaseStep("4.Check the app via browser",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), 
                                     test_html, "-H 'Pragma: no-cache'", 5, 9],
                expect_description="'%s' should be found in the web page" % (test_html),
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed()
        if case.testcase_status == 'FAILED':
            return self.failed()
        if case.testcase_status == 'ERROR':
            return self.incomplete()

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PhpSqliteSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
