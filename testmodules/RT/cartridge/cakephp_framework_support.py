"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]Cakephp framework support
https://tcms.engineering.redhat.com/case/122275/
"""

import os,sys
import testcase,common,OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge]Cakephp framework support"

        self.app_name = "cakephp"
        self.app_type = common.app_types["php"]
        self.git_repo = os.path.abspath(os.curdir)+"/"+self.app_name

        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s* "%(self.app_name))



class CakephpFrameworkSupport(OpenShiftTest):
    def test_method(self):

        # 1.Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an php app",
                common.create_app,
                function_parameters=[self.app_name,
                                     self.app_type,
                                     self.config.OPENSHIFT_user_email,
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Customize this app for cakephp
        self.steps_list.append(testcase.TestCaseStep("2.Customize this app for cakephp and Git push",
                    "cd "+self.git_repo+"/php/ && cp "+WORK_DIR+"/app_template/cakephp.tar.gz ./ && tar xzf cakephp.tar.gz && git add . && git commit -am t && git push",
                    expect_description="cakephp+git push should be installed successfully",
                    expect_return=0))

        # 3.Check app via browser
        def get_app_url(app_name):
            def closure():
                return  OSConf.get_app_url(self.app_name) + "/cakephp/"
            return closure

        test_html = "CakePHP: the rapid development php framework"
        self.steps_list.append(testcase.TestCaseStep("4.Check app via browser",
                    common.grep_web_page,
                    function_parameters=[get_app_url(self.app_name), test_html, "-H 'Pragma: no-cache'", 3, 9],
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
    suite.add_test(CakephpFrameworkSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
