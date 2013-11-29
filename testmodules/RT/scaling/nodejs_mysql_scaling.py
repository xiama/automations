#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US2006][Runtime][rhc-cartridge]Embed mysql to scalable apps: nodejs")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = 'nodejs' + common.getRandomString()
        self.app_type = common.app_types["nodejs"]
        self.random1 = common.getRandomString(10)
        
        common.env_setup()


    def finalize(self):
        pass

class NodejsScalingMysql(OpenShiftTest):

    def fill_mysql(self):
        time.sleep(20)
        app_url = OSConf.get_app_url(self.app_name)
        common.fetch_page("%s/data1.js"% app_url)
        common.fetch_page("%s/data1.js"% app_url)
        return 0

    def check_mysql_result(self, s_pattern):
        app_url = OSConf.get_app_url(self.app_name)
        url = "%s/show.js"% app_url
        return common.grep_web_page(url, s_pattern, delay=5, count=4)

    def update_mysql_credentials(self):
'''
        mysql = OSConf.get_embed_info(self.app_name, common.cartridge_types['mysql'])
        
        self.info("mysql credentials: %s"%mysql)

        try:
            self.info("Copy/modify template files")
            fr = open("%s/../cartridge/app_template/mysql/server.js"%WORK_DIR, 'r')
            s = fr.read()
            fr.close()

            s = s.replace("#mysql_host#", mysql['url'])
            s = s.replace("#mysql_port#", mysql['port'])
            s = s.replace("#mysql_user#", mysql['username'])
            s = s.replace("#mysql_passwd#", mysql['password'])
            s = s.replace("#mysql_dbname#", mysql['database'])
            s = s.replace("#str_random1#", self.random1)
            s = s.replace("#str_random2#", self.random1)

            fw = open("./%s/server.js" % self.app_name, 'w')
            fw.write(s)
            fw.close()
        except Exception as e:
            self.error(e)
            return False
'''
        return True

    def test_method(self):
        self.add_step("Create a scalable %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type, self.user_email, self.user_passwd, True, "./" + self.app_name, True],
            expect_description = "App should be created successfully",
            expect_return = 0)

        self.add_step("embed mysql to %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd ],
            expect_return = 0)

        self.add_step("Changing MySQL credentials",
            self.update_mysql_credentials,
            expect_description = "Operation must be successfull",
            expect_return = True)

        self.add_step("git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0)

        self.add_step("Pollute data into MySql",
            self.fill_mysql,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0)

        self.add_step("Check MySql Result",
            self.check_mysql_result,
            function_parameters = [self.random1],
            expect_description = "MySQL operation must be successfull",
            expect_return = 0)
        
        self.add_step("Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [ self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0)
        
        for i in range(1,4):
            self.add_step("Check MySql Result - again",
                self.check_mysql_result,
                function_parameters = [self.random1],
                expect_description = "MySQL operation must be successfull",
                expect_return = 0)

        self.add_step("Scale-down the application via Rest API",
            common.scale_down,
            function_parameters = [ self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0,
            try_interval=5,
            try_count=6)

        self.add_step("Check MySql Result - again",
            self.check_mysql_result,
            function_parameters = [self.random1],
            expect_description = "MySQL operation must be successfull",
            expect_return = 0)

        self.add_step("Remove mysql from %s" % self.app_name,
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
    suite.add_test(NodejsScalingMysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
