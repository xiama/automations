#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

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
        self.app_name = common.getRandomString(10)
        tcms_testcase_id= 121920
        try:
             self.app_type = self.config.test_variant
        except:
             self.app_type = 'php'

        tcms_testcase_id = 121920
        self.snapshot_file = "snapshot_%s.tar.gz" % self.app_name

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class SnapshotRestoreMongoDB(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a %s application" % self.app_type,
                                  common.create_app,
                                  function_parameters=[self.app_name, common.app_types[self.app_type], self.user_email, self.user_passwd, True],
                                  expect_return=0
				))

        self.steps_list.append(testcase.TestCaseStep("Embed with mongodb" ,
                                  common.embed,
                                  function_parameters=[self.app_name,'add-%s'%common.cartridge_types['mongodb'],self.user_email, self.user_passwd],
                                  expect_return=0
				))


        def modify_data(app_name, op, data):
            mongo_cmds= "echo 'db.items.%s(%s)' | mongo"%(op, data)
            if op=='find':
                mongo_cmds += ' | grep ObjectId '
            (status, output) = common.run_remote_cmd(app_name, mongo_cmds)

            return status

        self.steps_list.append(testcase.TestCaseStep("Insert same data into mongoDB",
                                  modify_data,
                                  function_parameters=[self.app_name,'insert', '{name: "eggs", quantity: 100, price: 1.50 }'],
                                  expect_return=0))

        '''steps.append(testcase.TestCaseStep("Embed with rockmongo",
                                  common.embed,
                                  function_parameters=[self.app_name,'add-%s'%common.cartridge_types['rockmongo'],self.user_email, self.user_passwd],
                                  expect_return=0))'''
        self.steps_list.append(testcase.TestCaseStep("Make snapshot",
                                  "rhc snapshot save %s -f %s -l %s -p '%s' %s"%(self.app_name, self.snapshot_file, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Drop same data from mongoDB",
                                  modify_data,
                                  function_parameters=[self.app_name, 'remove', '{name: "eggs", quantity: 100, price: 1.50 }'],
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Verify recent drop from mongoDB",
                                  modify_data,
                                  function_parameters=[self.app_name, 'find', '{name: "eggs", quantity: 100, price: 1.50 }'],
                                  expect_return=1))

        self.steps_list.append(testcase.TestCaseStep("Restore from snapshot",
                                  "rhc snapshot restore %s -f %s -l %s -p '%s' %s"%(self.app_name, self.snapshot_file, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Check if there are 100 eggs",
                                  modify_data,
                                  function_parameters=[self.app_name, 'find', '{name: "eggs", quantity: 100, price: 1.50 }'],
                                  expect_return=0))

        case = testcase.TestCase("[US1209][Runtime][cartridge]take snapshot and restore without new app for embedded mongodb",
                             self.steps_list)

        def cleaning():
            cmd="rm -rf %s; rm -f %s"%(self.app_name, self.snapshot_file)
            common.command_get_status(cmd)
            pass

        case.add_clean_up(cleaning)
        case.run()
	
	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreMongoDB)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
