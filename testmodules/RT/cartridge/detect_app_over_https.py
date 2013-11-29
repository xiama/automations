"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
1115] [rhc-cartridge]detect app come over https or http
https://tcms.engineering.redhat.com/case/122351/
"""
import os,sys,re

import testcase
import common
import OSConf
import rhtest
# user defined packages
import openshift

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1115] [rhc-cartridge]detect app come over https or http"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.test_variant = "php"

        self.app_name = self.test_variant.split('-')[0] + "https"
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        self.app_type = common.app_types[self.test_variant]
        self.steps_list = []
        tcms_testcase_id=122351
        common.env_setup()

    def finalize(self):
        pass

class DetectAppOverHttps(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep("Create an %s app" % (self.app_name),
                common.create_app,
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        type_to_cmd = {         
            "php"     : "cp -f %s/app_template/https/index.php %s/php/" % (WORK_DIR, self.git_repo),
            "jbossas" : "rm -f %s/src/main/webapp/index.html && cp -f %s/app_template/https/index.jsp %s/src/main/webapp/" % (self.git_repo, WORK_DIR, self.git_repo)}

        self.steps_list.append(testcase.TestCaseStep("Copy the corresponding app template to the git repo",
                type_to_cmd[self.test_variant],
                expect_description="Copy succeed",
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Git push the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="git push should succeed",
                expect_return=0))

        def get_app_url(self, proto):
            def closure():
                return proto+"://"+OSConf.get_app_url(self.app_name)
            return closure

        if self.test_variant == "php":
            regex = r'X-Forwarded-Proto </td><td class="v">http </td>'
        elif self.test_variant == "jbossas":
            regex = r'x-forwarded-proto:<BR>http<BR>'
        self.steps_list.append(testcase.TestCaseStep("Check the app through HTTP",
                common.grep_web_page,
                function_parameters=[get_app_url(self,"http"), regex, "-H 'Pragma: no-cache'", 3, 6],
                expect_description="X-Forwarded-Proto should be http",
                expect_return=0))

        if self.test_variant == "php":
            regex = r'X-Forwarded-Proto </td><td class="v">https </td>'
        elif self.test_variant == "jbossas":
            regex = r'x-forwarded-proto:<BR>https<BR>'
        self.steps_list.append(testcase.TestCaseStep("Check the app through HTTPS",
                common.grep_web_page,
                function_parameters=[get_app_url(self,"https"), regex, "-H 'Pragma: no-cache' -k", 3, 6],
                expect_description="X-Forwarded-Proto should be https",
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
    suite.add_test(DetectAppOverHttps)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
