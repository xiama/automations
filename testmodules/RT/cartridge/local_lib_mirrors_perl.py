"""
Linqing Lu
lilu@redhat.com
Dec 9, 2011

[US1309][rhc-cartridge]Create local lib mirrors for Perl framework
https://tcms.engineering.redhat.com/case/122395/
"""
import os,sys,re

import testcase, common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1309][rhc-cartridge]Create local lib mirrors for Perl framework"
        self.app = { 'name':'perltest', 'type':'perl-5.10' }
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app['name']))

class LocalLibMirrorsPerl(OpenShiftTest):
    def test_method(self):
        self.steps_list.append( testcase.TestCaseStep(
                "Create an %s app: %s" % (self.app['type'],self.app['name']),
                common.create_app,
                function_parameters = [self.app['name'], self.app['type']],
                expect_description = "App should be created successfully",
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep("Edit deplist.txt",
                "echo 'YAML' >> %s/deplist.txt" % self.app['name'],
                expect_description = "deplist.txt should be updated successfully",
                expect_return = 0))

        self.steps_list.append( testcase.TestCaseStep("git push",
                "cd %s && git commit -am test && git push" % self.app['name'],
                expect_string_list = ['Successfully installed YAML-', 'Fetching http.*perl'],
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

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LocalLibMirrorsPerl)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
