#!/usr/bin/env python
import os, sys

import testcase, common, OSConf
import rhtest
import database
import time
import random
# user defined packages
import openshift


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US994][rhc-cartridge] Configuration files refereceable in standalone.xml"
	self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_name = "standalone" + common.getRandomString(4)
        self.app_type = common.app_types["jbossas"]
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        self.app_uuid = ""

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        os.system('rm -rf %s*' % (self.app_uuid))


class ConfigurationFilesReferceableInStandaloneXml(OpenShiftTest):

    def check_softlink(self):
        self.app_uuid = OSConf.get_app_uuid(self.app_name)
        exp_str = "xx.xml -> /var/lib/openshift/%s/app-root/runtime/repo/.openshift/config/xx.xml" % (self.app_uuid)
        cmd = "cd %s/jbossas-7/jbossas-7/standalone/configuration && ls -l" % (self.app_uuid)
        (ret, output) = common.command_getstatusoutput(cmd)
        if ret == 0 and output.find(exp_str) != -1:
            self.info("Successfully find '%s' in the output" % (exp_str))
            return 0
        else:
            self.info("Failed to find '%s' in the output" % (exp_str))
            return 1

    def test_method(self):
        # 1.Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an jbossas app: %s" % (self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0,
        ))
        # 2.Make some changes to the git repo
        self.steps_list.append(testcase.TestCaseStep("2.Make some changes to the git repo",
                "touch %s/.openshift/config/xx.xml && [ -d %s/.openshift/config/modules/ ] || mkdir %s/.openshift/config/modules/" % (self.git_repo, self.git_repo, self.git_repo),
                expect_description="Git repo successfully modified",
                expect_return=0,
        ))
        # 3.Git push all the changes
        self.steps_list.append(testcase.TestCaseStep("3.Git push all the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="Git push should succeed",
                expect_return=0,
        ))
        # 4.Check app via browser
        self.steps_list.append(testcase.TestCaseStep("4.Check the app via browser",
                    common.check_web_page_output,
                    function_parameters=[self.app_name, ],
                    expect_description="The app should be available",
                    expect_return=0
        ))
        # 5.Save snapshot of this app and extract
        self.steps_list.append(testcase.TestCaseStep("5.Save snapshot of this app",
                "rhc snapshot save %s -l %s -p '%s' %s && tar xzf %s.tar.gz" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS, self.app_name),
                expect_description="Snapshot should be saved and extracted successfully",
                expect_return=0,
        ))
        # 6.Check snapshot to see soft link of configuration files
        self.steps_list.append(testcase.TestCaseStep("6.Check snapshot to see soft link of configuration files",
                self.check_softlink,
                expect_description="Soft link of configuration files should be found",
                expect_return=0,
        ))
        # 7.Remove config file in git repo and git push
        self.steps_list.append(testcase.TestCaseStep("7.Remove config file in git repo",
                "cd %s && git rm .openshift/config/xx.xml && git commit -am t && git push" % (self.git_repo),
                expect_description="Git push should succeed",
                expect_return=0,
        ))
        # 8.Remove <self.app_name>.tar.gz and the extracted dir
        self.steps_list.append(testcase.TestCaseStep("8.Remove <app_name>.tar.gz and the extracted dir",
                "rm -rf %s && rm -f %s.tar.gz" % (self.app_uuid, self.app_name),
                expect_description="<app_name>.tar.gz and the extracted dir should be removed",
                expect_return=0,
        ))
        # 9.Save snapshot again
        self.steps_list.append(testcase.TestCaseStep("9.Save snapshot again",
                "rhc snapshot save %s -l %s -p '%s' %s && tar xzf %s.tar.gz" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS, self.app_name),
                expect_description="Snapshot should be saved and extracted successfully",
                expect_return=0,
        ))
        # 10.Check snapshot to see soft link of configuration files disappear
        self.steps_list.append(testcase.TestCaseStep("10.Check snapshot to see soft link of configuration files disappear",
                "ls -l %s/jbossas-7/jbossas-7/standalone/configuration/xx.xml" % (self.app_uuid),
                expect_description="Soft link of configuration files should not be found",
                expect_return="!0",
                expect_string_list=["No such file or directory",],
        ))
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
    suite.add_test(ConfigurationFilesReferceableInStandaloneXml)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
