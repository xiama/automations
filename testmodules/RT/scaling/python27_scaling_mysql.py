#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase, common, OSConf
import rhtest
# user defined packages
import openshift
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = os.environ["OPENSHIFT_user_email"]
        self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_name = 'mypython' + common.getRandomString()
        self.rest_client = openshift.Openshift(host=self.config.instance_info['ip'],
                                               user=self.user_email, 
                                               passwd=self.user_passwd)
        self.app_type = common.app_types["python-2.7"]
        
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass

class PythonMysqlScaling(OpenShiftTest):
    def check_mysql_result(self, app_name):
        app_url = OSConf.get_app_url(app_name)
        return common.grep_web_page("http://%s/mysql" % app_url, "Tim Bunce, Advanced Perl DBI", "-H 'Pragma: no-cache'", 5, 4)

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Create a scalable %s app: %s" % (self.app_type, self.app_name),
            common.create_scalable_app,
            function_parameters = [self.app_name, self.app_type, self.user_email, self.user_passwd, True, "./" + self.app_name],
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
            "cp '%s/cartridge/app_template/mysql/applicationpython-2.7' '%s/wsgi/application'" % (WORK_DIR + "/../", self.app_name),
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))
        self.steps_list.append(testcase.TestCaseStep(
            "Install MySQL-python",
            "sed -i -e \"s/#\s*'MySQL-python',/'MySQL-python',/g\" %s/setup.py" %(self.app_name),
            expect_description = "Operaion must be successfull",
            expect_return = 0
        ))
        #5
        self.steps_list.append(testcase.TestCaseStep(
            "git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0
        ))

        #6
        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result",
            self.check_mysql_result,
            function_parameters = [ self.app_name ],
            expect_description = "MySQL operation must be successfull",
            expect_return = 0
        ))

        #7
        self.steps_list.append(testcase.TestCaseStep(
            "Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [ self.app_name ],
            expect_description = "Operation must be successfull",
            expect_return = 0
        ))

        for i in range(1,4):
            self.steps_list.append(testcase.TestCaseStep(
                "Check MySql Result - %d" % i,
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
            expect_return = 0,
            try_interval=5,
            try_count=6))

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

        case = testcase.TestCase("[US2005][Runtime][rhc-cartridge]Embed mysql to scalable apps: python", self.steps_list)
        case.run()
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PythonMysqlScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
