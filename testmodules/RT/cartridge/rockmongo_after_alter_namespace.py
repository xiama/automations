#!/usr/bin/env python
"""
Linqing Lu
lilu@redhat.com
Dec 12, 2011

[US1545][BusinessIntegration][embed_web_interface]use rockmongo after alter domain namespace 
https://tcms.engineering.redhat.com/case/123975/
"""

import os,sys,re,random,string
import testcase,common,OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1545][BusinessIntegration][embed_web_interface]use rockmongo after alter domain namespace"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name - used `php` as default")
            self.test_variant = 'python'

        self.app_name = common.getRandomString(14)
        self.domain_name = common.get_domain_name()
        self.new_domain_name = common.getRandomString(10)
        self.app_type = common.app_types[self.test_variant]
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        pass

class RockmongoAfterAlterNamespace(OpenShiftTest):

    def test_method(self):
        #1
        self.steps_list.append(testcase.TestCaseStep(
                "Create an %s app: %s" % (self.app_type, self.app_name),
                common.create_app,
                function_parameters = [self.app_name, self.app_type],
                expect_description = "App should be created successfully",
                expect_return = 0))

        #2
        self.steps_list.append(testcase.TestCaseStep("Alter the domain name",
                common.alter_domain,
                function_parameters=[self.new_domain_name, 
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd],
                expect_description="Domain was altered successfully",
                expect_return=0))

        #3
        self.steps_list.append(testcase.TestCaseStep(
                "embed mongodb into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-%s"%common.cartridge_types['mongodb']],
                expect_return = 0))

        #4
        self.steps_list.append(testcase.TestCaseStep(
                "embed rockmongo into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-%s"%common.cartridge_types['rockmongo']],
                expect_return = 0))

        #5
        self.steps_list.append(testcase.TestCaseStep(
                "check whether rockmongo working",
                self.check_rockmongo,
                expect_return = 0))

        #6
        self.steps_list.append(testcase.TestCaseStep("Alter the domain name",
                common.alter_domain,
                function_parameters=[self.domain_name, 
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd],
                expect_description="Domain was altered successfully",
                expect_return=0))

        #7
        self.steps_list.append(testcase.TestCaseStep(
                "check whether rockmongo working",
                self.check_rockmongo,
                expect_return = 0))


        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def check_rockmongo(self, negative = False):
        keyword = "RockMongo"
        if negative:
            keyword = "503 Service Temporarily Unavailable"
        url = OSConf.get_embed_info(self.app_name, common.cartridge_types["rockmongo"], "url")+"/index.php?action=login.index"
        ret = common.grep_web_page(url, keyword, options="-k -H 'Pragma: no-cache'", delay=5, count=10)
        os.system("curl -k -H 'Pragma: no-cache' %s"% url)
        return ret


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RockmongoAfterAlterNamespace)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
