#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase, common, OSConf
import rhtest
# user defined packages
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = 'myruby' + common.getRandomString(5)
        try:
            variant = self.get_variant()
        except:
            variant = 'ruby'
        self.app_type = common.app_types[variant]
        self.info("VARIANT: %s"%variant)
        common.env_setup()
        self.domain_name = common.get_domain_name()
        self.steps_list = []

    def finalize(self):
        pass
    
class RubyMysqlScaling(OpenShiftTest):
    def check_mysql_result(self):
        app_url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page("http://%s/mysql" % app_url, "Tim Bunce, Advanced Perl DBI", "-H 'Pragma: no-cache'", 5, 6)

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Create a scalable %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type, self.user_email, self.user_passwd, True, "./" + self.app_name, True],
            expect_description = "App should be created successfully",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "embed mysql to %s" % self.app_name,
            common.embed,
            expect_description = "Embedding mysql should pass",
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd ],
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Copy template files",
            "cp %s/cartridge/app_template/mysql/config.ru %s/" % (WORK_DIR + "/../", self.app_name),
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_description = "git push should pass without errors",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result",
            self.check_mysql_result,
            expect_description = "Checking MySQL operation via web must pass",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [ self.app_name,],
            expect_description = "The application must scale-up successfully",
            expect_return = 0
        ))
        
        for i in range(1,4):
            self.steps_list.append(testcase.TestCaseStep(
                "Check MySql Result - %d" % i,
                self.check_mysql_result,
                expect_description = "Checking MySQL operation via web must be successfull",
                expect_return = 0
            ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-down the application via Rest API",
            common.scale_down,
            function_parameters = [ self.app_name,],
            expect_description = "The application must scale-down successfully",
            expect_return = 0,
            try_interval=5,
            try_count=6,
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result - again",
            self.check_mysql_result,
            expect_description = "Checking MySQL operation via web must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Remove mysql from %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "remove-" + common.cartridge_types["mysql"] ],
            expect_description = "Remoevd mysql should pass",
            expect_return = 0
        ))

        case = testcase.TestCase("[US2006][Runtime][rhc-cartridge]Embed mysql to scalable apps: ruby", self.steps_list)
        case.run()
    
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RubyMysqlScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
