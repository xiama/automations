"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]PHP Framework Support
https://tcms.engineering.redhat.com/case/122283/
"""
import os,sys,re,time

import testcase
import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[rhc-cartridge]PHP Framework Support"
        self.app_name = "phpframework"
        self.app_type = common.app_types["php"]
        self.git_repo = "./%s" % (self.app_name)
        tcms_testcase_id=122283
        common.env_setup()

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class PhpFrameworkSupport(OpenShiftTest):
    def test_method(self):

        # 1.Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an php app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Make some changes to the git repo
        self.steps_list.append(testcase.TestCaseStep("2.Make some changes to the git repo",
                "rm -rf %s/php/index.php && cp -f %s/app_template/php.template %s/php/index.php && cd %s && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR, self.git_repo, self.git_repo),
                expect_description="Git repo successfully modified",
                expect_return=0))

        # 3.Check app via browser
        test_html = "The Times-Tables"
        
        self.steps_list.append(testcase.TestCaseStep("3.Check the app via browser",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), 
                                    test_html, "-H 'Pragma: no-cache'", 3, 9],
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
    suite.add_test(PhpFrameworkSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
