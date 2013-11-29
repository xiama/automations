"""
Linqing Lu
lilu@redhat.com
Dec 12, 2011

[US1545][BusinessIntegration][embed_web_interface]Control rockmongo using 'rhc cartridge'
https://tcms.engineering.redhat.com/case/123974/
"""
import os,sys,re

import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1545][BusinessIntegration][embed_web_interface]Control rockmongo using 'rhc cartridge'"
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'jbossews'
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        pass

class RhcCtlRockmongo(OpenShiftTest):

    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type],
            expect_description = "App should be created successfully",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "embed mongodb into app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "add-mongodb-2.2"],
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "embed rockmongo into app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "add-rockmongo-1.1"],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "check whether rockmongo working",
            self.check_rockmongo,
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "stop rockmongo of app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "stop-rockmongo-1.1"],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "check whether rockmongo stopped",
            self.check_rockmongo,
            function_parameters = ['True'],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "start rockmongo in app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "start-rockmongo-1.1"],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "check whether rockmongo working",
            self.check_rockmongo,
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "start rockmongo in app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "restart-rockmongo-1.1"],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "check whether rockmongo working",
            self.check_rockmongo,
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
            "start rockmongo in app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "reload-rockmongo-1.1"],
            expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep(
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
        ret = common.grep_web_page(url, keyword, options="-k -H 'Pragma: no-cache'", delay=8, count=10)
        os.system("curl -k -H 'Pragma: no-cache' %s"% url)
        return ret

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcCtlRockmongo)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
