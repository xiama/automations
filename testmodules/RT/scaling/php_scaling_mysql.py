#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase, common, OSConf
import rhtest
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = os.environ["OPENSHIFT_user_email"]
        self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_name = 'myphp' + common.getRandomString()
        self.app_type = common.app_types["php"]
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass

class PHPMysqlScaling(OpenShiftTest):
    def check_mysql_result(self, app_name):
        app_url = OSConf.get_app_url(app_name)
        return common.grep_web_page("http://%s/mysql.php" % app_url, "Tim Bunce, Advanced Perl DBI", "-H 'Pragma: no-cache'", 5, 4)

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
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd ],
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Copy template files",
            "cp %s/cartridge/app_template/mysql/mysql.php %s/php/" % (WORK_DIR + "/../", self.app_name),
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result",
            self.check_mysql_result,
            function_parameters = [ self.app_name ],
            expect_description = "MySQL operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [ self.app_name ],
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))
        
        for i in range(1,4):
            self.steps_list.append(testcase.TestCaseStep(
                "Check MySql Result - again",
                self.check_mysql_result,
                function_parameters = [ self.app_name ],
                expect_description = "MySQL operation must be successfull",
                expect_return = 0
            ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-down the application via Rest API",
            common.scale_down,
            function_parameters = [ self.app_name ],
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result - again",
            self.check_mysql_result,
            function_parameters = [ self.app_name ],
            expect_description = "MySQL operation must be successfull",
            expect_return = 0
        ))

        self.steps_list.append(testcase.TestCaseStep(
            "Remove mysql from %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "remove-" + common.cartridge_types["mysql"] ],
            expect_description = "Operation must be successfull",
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
    suite.add_test(PHPMysqlScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
