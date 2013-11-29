#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

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
        try:
            self.test_variant = self.config.test_variant
        except:
            print "OPENSHIFT_test_name environment variable is not set. Running test with default php"
            self.test_variant = "zend"

        self.app_type = common.app_types[self.test_variant]
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(5)
        tcms_testcase_id = 107695
        if self.test_variant == "perl":
            file_name = "index.pl"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/perl/index.pl" %(self.app_name)
            url_path1 = "index.pl?action=create"
            url_path2 = "index.pl?action=modify"
            url_path3 = "index.pl"
        elif self.test_variant in ("php", "zend"):
            file_name = "index.php"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/php/index.php" %(self.app_name)
            url_path1 = "index.php?action=create"
            url_path2 = "index.php?action=modify"
            url_path3 = "index.php"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            file_name = "rack/*"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python", "wsgi"):
            file_name = "application.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant == "python-2.7":
            file_name = "applicationpython-2.7.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant == "python-3.3":
            file_name = "applicationpython-3.3.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("jbossas", "jbosseap", "jbossews", "jbossews2"):
            file_name = "test.jsp"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        else:
            raise rhtest.TestIncompleteError("Uknown variant name")

        self.file_name = file_name
        self.target_file = target_file
        self.source_file = source_file
        self.url_path1 = url_path1
        self.url_path2 = url_path2
        self.url_path3 = url_path3
   
        tcms_testcase_id=107695
    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class SnapshotRestoreDataDirToExistingApp(OpenShiftTest):
    def test_method(self):

        step = testcase.TestCaseStep("Create a %s application" %(self.app_type),
                                  common.create_app,
                                  function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                                  expect_return=0,
                                  expect_description="App should be created successfully"
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Copying test files to app git repo",
                                  "cp -f %s %s" %(self.source_file, self.target_file),
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Do git commit",
                                 "cd %s && git add . && git commit -m test && git push" %(self.app_name),
                                 expect_return=0,
                                 expect_description="File and directories are added to your git repo successfully"
                                )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Get app url",
                                  OSConf.get_app_url,
                                  function_parameters = [self.app_name]
                                 )
        self.steps_list.append(step)

        def verify(suffix, str_l):
            url=OSConf.get_app_url(self.app_name)
            return common.grep_web_page("%s/%s"%(url,suffix), str_l )

        step = testcase.TestCaseStep("Access app's URL to create files in OPENSHIFT_DATA_DIR directory",
                                  verify,
                                  function_parameters=[self.url_path1, ["Welcome", "RESULT=0"]],
                                  expect_return=0,
                                  try_interval=12,
                                  try_count=10)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Take snapshot",
                                  "rhc snapshot save %s -f %s -l %s -p %s %s" %(self.app_name, "%s.tar.gz"%(self.app_name), self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0
                                 )
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Access app's URL to modify files in OPENSHIFT_DATA_DIR directory",
                                  verify,
                                  function_parameters=[self.url_path2, ["Welcome", "RESULT=0"]],
                                  expect_return=0,
                                  try_interval=12,
                                  try_count=10
                                 )
#        self.steps_list.append(step)

        step = testcase.TestCaseStep("Restore app from snapshot",
                                  "rhc snapshot restore %s -f %s -l %s -p '%s' %s" %(self.app_name, "%s.tar.gz"%(self.app_name), self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                                  expect_return=0
                                 )
        self.steps_list.append(step)


        step = testcase.TestCaseStep("Access app's URL to check OPENSHIFT_DATA_DIR dir is restored",
                                  verify,
                                  function_parameters=[self.url_path3, ["Welcome", "snapshot_restore_data_dir_test1"]],
                                  expect_return=0,
                                  try_interval=12,
                                  try_count=10
                                 )
        self.steps_list.append(step)


        case = testcase.TestCase("[US566][rhc-client] Archive/Restore data to updated application\n[rhc-client]Create snapshot using rhc snapshot",
                             self.steps_list
                            )
        case.run()

	
	if case.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if case.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreDataDirToExistingApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
