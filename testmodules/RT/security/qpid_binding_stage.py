"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[security]Security - QPID fuzzing
https://tcms.engineering.redhat.com/case/122335/?from_plan=4962
"""

import os, sys

import rhtest
import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    ITEST="STG"
    def initialize(self):
        self.summary = "QPID fuzzing"
        #TODO: check the environment either STG or DEV
        self.app_type = common.app_types["php"]
        self.app_name = "SecurityTestApp"

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class QPIDbinding(OpenShiftTest):
    def test_method(self):
        self.info("Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App should be created successfully")

        source_file = "%s/data/qpid_fuzzing_stage.php" %(WORK_DIR)
        target_file = "%s/php/index.php" %(self.app_name)

        self.info("2.Copying test files to app git repo") 
        ret = common.command_get_status("cp -f %s %s" %(source_file, target_file))
        self.assert_equal(ret, 0)

        self.info("3. Do git commit") 
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name)) 

        self.assert_equal(ret, 0, "File and directories are added to your git repo successfully")

        self.info("4. Get app url") 
        app_url = OSConf.get_app_url(self.app_name)

        self.info("Access app's URL to tigger test") 
        ret = common.grep_web_page("%s/index.php?action=create"%app_url, "###RESULT###: PASS")
        self.assert_equal(ret, 0)

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QPIDbinding)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
