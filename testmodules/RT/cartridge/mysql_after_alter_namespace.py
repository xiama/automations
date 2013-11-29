#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]test mysql works well after altering namespace
https://tcms.engineering.redhat.com/case/122288/
"""


import os
import sys
import re
import string
import random
import testcase
import common
import OSConf
import rhtest
import openshift

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[rhc-cartridge]test mysql works well after altering namespace"
        try:
            self.test_variant = self.config.test_variant
            self.info("Missing OPENSHIFT_test_name, using `ruby` as default.")
        except:
            self.test_variant = 'ruby'

        self.new_domain_name = common.getRandomString(10)

        self.app_name = "app"+self.test_variant
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        self.domain_name = common.get_domain_name()
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class MysqlAfterAlterNamespace(OpenShiftTest):
    def test_method(self):
        #1
        self.steps_list.append(testcase.TestCaseStep("1.Create an express app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        #2
        self.steps_list.append(testcase.TestCaseStep("2.Embed mysql to the app",
                common.embed,
                function_parameters=[self.app_name, "add-mysql-5.1", self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="mysql cartridge is embedded successfully",
                expect_return=0))

        #3
        cmd_prefix = "unalias cp ; "
        cmd_dict = {
            "jbossas": "cp -f %s/app_template/mysql/mysql.jsp %s/src/main/webapp/" % (WORK_DIR, self.git_repo),
            "php"    : "cp -f %s/app_template/mysql/mysql.php %s/php/" % (WORK_DIR, self.git_repo),
            "perl"   : "cp -f %s/app_template/mysql/mysql.pl %s/perl/" % (WORK_DIR, self.git_repo),
            "python" : "cp -f %s/app_template/mysql/application %s/wsgi/" % (WORK_DIR, self.git_repo),
            "ruby"   : "cp -f %s/app_template/mysql/config.ru %s/" % (WORK_DIR, self.git_repo)}

        cmd = ''.join((cmd_prefix, cmd_dict[self.test_variant]))
        self.steps_list.append(testcase.TestCaseStep("3.Copy the corresponding app template to the app repo",
                cmd,
                expect_description="Copy succeeded",
                expect_return=0))

        #4
        self.steps_list.append(testcase.TestCaseStep(
                "4.Change the mysql url, username, password, database name to the app's ones",
                "%s",
                string_parameters=[self.get_cmd()],
                expect_description="Change succeeded",
                expect_return=0))

        if self.test_variant in ("python", "ruby"):
            suffix = "mysql"
        elif self.app_type.find("php") != -1:
            suffix = "mysql.php"
        elif self.app_type.find("jboss") != -1:
            suffix = "mysql.jsp"
        elif self.app_type.find("perl") != -1:
            suffix = "mysql.pl"

        def get_app_url(app_name, suffix):
            def closure():
                url = OSConf.get_app_url(app_name)
                return url+"/"+suffix
            return closure

        #5
        self.steps_list.append(testcase.TestCaseStep("5.Access the app to check if mysql works",
                common.grep_web_page,
                function_parameters=[get_app_url(self.app_name, suffix), 
                                     "Tim Bunce, Advanced Perl DBI", 
                                     "-H 'Pragma: no-cache'", 5, 6],
                expect_description="mysql works well",
                expect_return=0))
    
        #6
        self.steps_list.append(testcase.TestCaseStep("6.Alter the domain name",
            common.alter_domain,
            function_parameters=[self.new_domain_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
            expect_description="Domain was altered successfully",
            expect_return=0))

        #7
        self.steps_list.append(testcase.TestCaseStep("7.Access the app again to check if mysql still works",
                common.grep_web_page,
                function_parameters=[get_app_url(self.app_name,suffix), 
                                     "Tim Bunce, Advanced Perl DBI", 
                                     "-H 'Pragma: no-cache'", 5, 6],
                expect_description="mysql still works well",
                expect_return=0))
        #8
        self.steps_list.append(testcase.TestCaseStep("8.Change the domain name back",
                common.alter_domain,
                function_parameters=[self.domain_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="Domain was changed back successfully",
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

    def get_cmd(self):
        def closure():
            mysql_url = OSConf.default.conf['apps'][self.app_name]['embed']['mysql-5.1']['url']
            mysql_user = OSConf.default.conf['apps'][self.app_name]['embed']['mysql-5.1']['username']
            mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed']['mysql-5.1']['password']
            mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed']['mysql-5.1']['database']
            cmd_dict = {
                "jbossas": "cd %s" % (self.git_repo),
                "php"    : "cd %s/php && sed -i -e 's/changeme_url/%s/g' mysql.php && sed -i -e 's/changeme_username/%s/g' mysql.php && sed -i -e 's/changeme_password/%s/g' mysql.php && sed -i -e 's/changeme_db/%s/g' mysql.php" % (self.git_repo, mysql_url, mysql_user, mysql_passwd, mysql_dbname),
                "perl"   : "cd %s/perl && sed -i -e 's/changeme_url/%s/g' mysql.pl && sed -i -e 's/changeme_username/%s/g' mysql.pl && sed -i -e 's/changeme_password/%s/g' mysql.pl && sed -i -e 's/changeme_db/%s/g' mysql.pl" % (self.git_repo, mysql_url, mysql_user, mysql_passwd, mysql_dbname),
                "python" : "cd %s/wsgi && sed -i -e 's/changeme_url/%s/g' application && sed -i -e 's/changeme_username/%s/g' application && sed -i -e 's/changeme_password/%s/g' application && sed -i -e 's/changeme_db/%s/g' application" % (self.git_repo, mysql_url, mysql_user, mysql_passwd, mysql_dbname),
                "ruby"   : "cd %s && sed -i -e 's/changeme_url/%s/g' config.ru && sed -i -e 's/changeme_username/%s/g' config.ru && sed -i -e 's/changeme_password/%s/g' config.ru && sed -i -e 's/changeme_db/%s/g' config.ru" % (self.git_repo, mysql_url, mysql_user, mysql_passwd, mysql_dbname)}
            cmd_postfix = " && git add . ; git commit -am t && git push"
            cmd = ''.join((cmd_dict[self.test_variant], cmd_postfix))
            return cmd

        return closure

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MysqlAfterAlterNamespace)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
