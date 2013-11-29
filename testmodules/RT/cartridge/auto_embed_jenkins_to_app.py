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
	self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_type1 = "ruby-1.8"
        self.app_name1 = "testapp1"
        self.app_type2 = "python-2.6"
        self.app_name2 = "testapp2"

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class AutoEmbedJenkinsToApp(OpenShiftTest):
    def test_method(self):
        step = testcase.TestCaseStep("Get 'rhc app create' help output to make sure it supoort auto enable jenkins",
                                  "rhc help app create",
                                  expect_return=0,
                                  expect_string_list=['Create an application', 'enable-jenkins \[NAME\]']
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create app with --enable-jenkins option",
                                  "rhc app create %s %s -l %s -p '%s' --enable-jenkins %s" %(self.app_name1, self.app_type1, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_description="App with jenkins created success",
                                  expect_return=0,
                                  expect_string_list=["in Jenkins server"]
                                  #expect_string_list=["Jenkins client 1.4 has been added to"]
                                  )
#                                  expect_string_list=['Jenkins created successfully']
#                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Get user info to check jenkins app be listed",
                                  "rhc domain show -l %s -p '%s' %s" %(self.user_email,self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0,
                                  expect_string_list=['jenkins-1', 'applications in your domain', '%s-build' %(self.app_name1)]
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Do some change in app repo, and git push to trigger jenkins build",
                                  "cd %s && touch test && git add test && git commit -a -m 'update' && git push " %(self.app_name1),
                                  expect_return=0,
                                  expect_string_list=['Executing Jenkins build', 'Waiting for build to schedule', 'SUCCESS']
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Delete one app to release app quota for next step",
                                    "rhc app delete %s -l %s -p '%s' --confirm %s" %(self.app_name1, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                    expect_return=0
                                   )
        self.steps_list.append(step)
        step = testcase.TestCaseStep("Delete builder app to release app quota for next step",
                                    "rhc app delete %s -l %s -p '%s' --confirm %s" %(self.app_name1 + 'bldr', self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                    expect_return=0
                                   )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Create another app without --enable-jenkins option",
                                  "rhc app create %s %s -l %s -p '%s' %s" %(self.app_name2, self.app_type2, self.user_email,self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Get user info to check jenkins app be listed",
                                  "rhc domain show -l %s -p '%s' %s" %(self.user_email,self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0,
                                  expect_string_list=[self.app_name2],
                                  unexpect_string_list=['%s-build' %(self.app_name2)]
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Do some change in app repo, and git push",
                                  "cd %s && touch test && git add test && git commit -a -m 'update' && git push " %(self.app_name2),
                                  expect_description="There should NO jenkins build",
                                  expect_return=0,
                                  unexpect_string_list=['Waiting for build to schedule', 'Executing Jenkins build']
                                 )
        self.steps_list.append(step)

        case = testcase.TestCase("[US1279] [rhc-client] Automatically embed jenkins to your application via --enable-jenkins option of rhc cliet tools",
                            self.steps_list)

        case.add_clean_up(OSConf.initial_conf,function_parameters=[])
        case.run()

	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AutoEmbedJenkinsToApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
