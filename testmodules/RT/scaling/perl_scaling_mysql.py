#!/usr/bin/env python
import os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import common
import OSConf
import rhtest
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US2004][Runtime][rhc-cartridge]Embed mysql to scalable apps: perl")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = 'myperl' + common.getRandomString()
        self.app_type = common.app_types["perl"]
        
        common.env_setup()

    def finalize(self):
        pass


class PerlScalingMysql(OpenShiftTest):
    def check_mysql_result(self):
        app_url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page("http://%s/mysql.pl" % app_url, "Tim Bunce, Advanced Perl DBI", "-H 'Pragma: no-cache'", 5, 4)

    def test_method(self):
        self.add_step(
            "Create a scalable %s app: %s" % (self.app_type, self.app_name),
            common.create_scalable_app,
            function_parameters = [self.app_name, self.app_type, self.user_email, self.user_passwd, True],
            expect_description = "App should be created successfully",
            expect_return = 0)

        self.add_step(
            "embed mysql to %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd ],
            expect_return = 0)

        self.add_step(
            "Copy template files",
            "cp %s/cartridge/app_template/mysql/mysql.pl %s/perl/mysql.pl" % (WORK_DIR + "/../", self.app_name),
            expect_description = "Operation must be successfull",
            expect_return = 0)

        self.add_step(
            "git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0)

        self.add_step(
            "Check MySql Result",
            self.check_mysql_result,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0)

        self.add_step(
            "Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0,
            try_count=3)

        for i in range(1,4):
            self.add_step(
                "Check MySql Result - %d" % i,
                self.check_mysql_result,
                expect_description = "MySQL operation must be successfull",
                expect_return = 0)

        self.add_step(
            "Scale-down the application via Rest API",
            common.scale_down,
            function_parameters = [self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0,
            try_interval=5,
            try_count=6)

        self.add_step(
            "Check MySql Result - again",
            self.check_mysql_result,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0)

        self.add_step(
            "Remove mysql from %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "remove-" + common.cartridge_types["mysql"] ],
            expect_description = "Operation must be successfull",
            expect_return = 0)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)
    

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PerlScalingMysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
